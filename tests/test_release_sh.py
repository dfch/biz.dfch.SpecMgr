# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the gate helpers of `scripts/release.sh` (the v0.35.0 release
regressions: the dev CI gate matching the wrong workflow, the PR-check
polling failing fast on pending checks, and the post-merge PR close
failing on an already-merged PR).

The post-merge close also pins the v0.36.0 async-merge race (issue #213):
the PR-state read can come back empty/stale before GitHub's server-side
detection flips the PR to MERGED, so `close_pr_if_open` retries the read
with a bounded backoff and re-verifies the state after a failed
`gh pr close`. For these cases the fake `gh` shim answers the state from
a per-call sequence (a flip counter in the `run_<id>_flip`/`run_<id>_views`
style) and its `pr close` branch fails with a recorded message/exit code
when one is seeded.

The release-notes stage additionally pins the 2026-10-22 revert of the
release-name behaviour (SOP 98537416 Updates): the stage PATCHes the
notes only (no `name=` field), treats a matching stored body as done
regardless of the stored name, and rejects a second positional.

`release.sh` is a bash file; each test sources its functions in a
throwaway `bash -c` process (the file's `BASH_SOURCE` dispatch guard keeps
a source from running `main`) and intercepts every `gh` call with a fake
`gh` shim that answers from JSON fixtures in a per-test state directory.
No network access is needed.
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SH = REPO_ROOT / "scripts" / "release.sh"

GH_SHIM = """#!/usr/bin/env bash
# Fake `gh` for tests/test_release_sh.py (state dir: $RELEASE_TEST_STATE).
S="${RELEASE_TEST_STATE:?RELEASE_TEST_STATE must be set by the test}"
printf 'gh %s\\n' "$*" >>"$S/gh_calls.log"
if [ $# -eq 0 ]; then exit 0; fi
cmd="$1"; shift
case "$cmd" in
  run)
    sub="${1:-}"; shift || true
    case "$sub" in
      list)
        cat "$S/run_list.json"
        ;;
      view)
        id="${1:-}"; shift || true
        prog=""
        while [ $# -gt 0 ]; do
          if [ "$1" = "--jq" ]; then shift; prog="${1:-}"; fi
          shift || true
        done
        views=0
        if [ -f "$S/run_${id}_views" ]; then views=$(cat "$S/run_${id}_views"); fi
        views=$((views + 1))
        printf '%s' "$views" >"$S/run_${id}_views"
        flip=1
        if [ -f "$S/run_${id}_flip" ]; then flip=$(cat "$S/run_${id}_flip"); fi
        if [ "$views" -le "$flip" ]; then f="$S/run_${id}_inprogress.json"; else f="$S/run_${id}_done.json"; fi
        if [ ! -f "$f" ]; then echo "shim: missing fixture $f" >&2; exit 3; fi
        if [ -n "$prog" ]; then jq -r "$prog" "$f"; else cat "$f"; fi
        ;;
      *)
        echo "shim: unsupported run subcommand: $sub" >&2; exit 3
        ;;
    esac
    ;;
  pr)
    sub="${1:-}"; shift || true
    case "$sub" in
      checks)
        c=0
        if [ -f "$S/pr_checks_count" ]; then c=$(cat "$S/pr_checks_count"); fi
        c=$((c + 1))
        printf '%s' "$c" >"$S/pr_checks_count"
        outf="$S/pr_checks_${c}.out"
        rcf="$S/pr_checks_${c}.rc"
        if [ ! -f "$outf" ]; then outf="$S/pr_checks_last.out"; rcf="$S/pr_checks_last.rc"; fi
        if [ ! -f "$outf" ]; then echo "shim: no pr-checks fixture for call $c" >&2; exit 3; fi
        cat "$outf"
        exit "$(cat "$rcf")"
        ;;
      close)
        if [ -f "$S/close_rc" ]; then
          [ -f "$S/close_msg" ] && cat "$S/close_msg" >&2
          exit "$(cat "$S/close_rc")"
        fi
        exit 0
        ;;
      *)
        echo "shim: unsupported pr subcommand: $sub" >&2; exit 3
        ;;
    esac
    ;;
  api)
    case " $* " in
      *" --method PATCH "*)
        exit 0
        ;;
    esac
    case "$*" in
      *releases/tags/*)
        [ -f "$S/release.json" ] || { echo "shim: missing fixture release.json" >&2; exit 3; }
        cat "$S/release.json"
        exit 0
        ;;
    esac
    # Merged-PR search (feat-233 closeout gate): the exact head-ref lookup
    # pulls?state=closed&head={owner}:<ref>&per_page=100 and the one-shot
    # REQ-011 page scan pulls?state=closed&per_page=100. Both answer from
    # the pulls_closed.json fixture, whose PRs carry number, head.ref,
    # merged_at, and merge_commit_sha; the exact lookup emulates the
    # server-side head filter (the documented user:ref colon form).
    search=""
    for a in "$@"; do
      case "$a" in
        *pulls?state=closed*) search="$a" ;;
      esac
    done
    if [ -n "$search" ]; then
      [ -f "$S/pulls_closed.json" ] || { echo "shim: missing fixture pulls_closed.json" >&2; exit 3; }
      case "$search" in
        *"head={owner}:"*)
          ref="${search#*"head={owner}:"}"
          ref="${ref%%&*}"
          jq --arg ref "$ref" '[.[] | select(.head.ref == $ref)]' "$S/pulls_closed.json"
          ;;
        *)
          cat "$S/pulls_closed.json"
          ;;
      esac
      exit 0
    fi
    pull=""
    for a in "$@"; do
      case "$a" in
        *pulls/*) pull="$a" ;;
      esac
    done
    n="${pull##*/pulls/}"
    if [ -f "$S/pull_${n}_flip" ]; then
      views=0
      if [ -f "$S/pull_${n}_views" ]; then views=$(cat "$S/pull_${n}_views"); fi
      views=$((views + 1))
      printf '%s' "$views" >"$S/pull_${n}_views"
      flip=$(cat "$S/pull_${n}_flip")
      if [ "$views" -le "$flip" ]; then f="$S/pull_${n}_stale"; else f="$S/pull_${n}_final"; fi
      if [ -f "$f" ]; then cat "$f"; else echo "open"; fi
    elif [ -f "$S/pull_${n}_state" ]; then cat "$S/pull_${n}_state"; else echo "open"; fi
    ;;
  auth)
    exit 0
    ;;
  *)
    echo "shim: unsupported gh command: $cmd" >&2; exit 3
    ;;
esac
"""


def _clean_git_env() -> dict[str, str]:
    """A copy of the current environment with every `GIT_*` variable removed.

    Every `git`/`bash` subprocess this test suite spawns for its own
    throwaway fixture repos must use this, never the ambient environment
    unmodified: when this suite itself runs as part of `git commit`'s own
    pre-commit hook (the exact way an agent hits this), git exports
    `GIT_DIR`/`GIT_INDEX_FILE`/`GIT_WORK_TREE`/`GIT_PREFIX`/
    `GIT_CONFIG_PARAMETERS` (and friends) into the hook's whole process
    tree -- pre-commit, then `pytest`, then every subprocess it spawns.
    Left unsanitized, those variables silently redirect a fixture's "fresh
    temp repo" git commands onto the *real* enclosing repository instead
    (e.g. `checkout -b dev` then hits the real repo's actual `dev` branch
    and fails with "fatal: A branch named 'dev' already exists.", or a
    fixture commit collides with the real commit-in-progress's staged-only
    index lock file) -- confusing failures with nothing to do with the
    fixture's own git history.
    """
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def _git(args: list[str], cwd: Path) -> str:
    """Run a git command in `cwd` and return its stripped stdout."""
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=_clean_git_env())
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


class ReleaseShGateTestCase(unittest.TestCase):
    """Tests for `release.sh`'s dev CI / PR check gate helpers."""

    def setUp(self):
        """Create the per-test state dir and the fake `gh` shim."""
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.state = self.tmp / "state"
        self.state.mkdir()
        self.shim_dir = self.tmp / "shim"
        self.shim_dir.mkdir()
        shim = self.shim_dir / "gh"
        shim.write_text(GH_SHIM)
        os.chmod(shim, 0o755)

    def tearDown(self):
        """Remove the per-test temp directory."""
        self._tmp.cleanup()

    def write_state(self, name: str, content: str) -> None:
        """Write one fixture file into the shim state dir."""
        (self.state / name).write_text(content)

    def run_release(self, body: str, git_repo: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Source `release.sh` and run `body` under the fake `gh` (POLL_INTERVAL=1)."""
        script = (
            "set -euo pipefail\n"
            f'export RELEASE_TEST_STATE="{self.state}"\n'
            f'export PATH="{self.shim_dir}:$PATH"\n'
            f'source "{RELEASE_SH}"\n'
            "POLL_INTERVAL=1\n"
        )
        if git_repo is not None:
            script += f'cd "{git_repo}"\n'
        script += body
        return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=300, env=_clean_git_env())

    def make_repo(self) -> tuple[Path, str]:
        """Create a bare origin plus a dev checkout with one commit; return (repo, sha)."""
        bare = self.tmp / "origin.git"
        repo = self.tmp / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True, env=_clean_git_env())
        _git(["init"], repo)
        # -B (not -b): `git init`'s own default initial branch may already be
        # "dev" if the environment has `init.defaultBranch=dev` configured
        # (plausible for a contributor to this repo, whose default branch is
        # "dev") -- `checkout -b dev` would then fail with "fatal: A branch
        # named 'dev' already exists.". `-B` creates-or-resets regardless.
        _git(["checkout", "-B", "dev"], repo)
        (repo / "file.txt").write_text("x\n")
        _git(["add", "."], repo)
        _git(["-c", "user.email=test@test", "-c", "user.name=test", "commit", "-m", "c1"], repo)
        _git(["remote", "add", "origin", str(bare)], repo)
        _git(["push", "origin", "dev"], repo)
        return repo, _git(["rev-parse", "HEAD"], repo)

    def graph_update_run(self, sha: str) -> dict[str, object]:
        """A completed dependabot Graph Update run on dev (must never be picked)."""
        return {
            "databaseId": 999,
            "headSha": sha,
            "headBranch": "dev",
            "event": "dynamic",
            "name": "Graph Update: uv in /.",
            "status": "completed",
            "conclusion": "success",
        }

    def lint_test_run(
        self, sha: str, run_id: int = 100, status: str = "in_progress", conclusion: str | None = None
    ) -> dict[str, object]:
        """A Lint and Test push run on dev (the only run the gate may pick)."""
        return {
            "databaseId": run_id,
            "headSha": sha,
            "headBranch": "dev",
            "event": "push",
            "name": "Lint and Test",
            "status": status,
            "conclusion": conclusion,
        }

    def write_run_fixtures(self, run_id: int, flip: int = 1) -> None:
        """Give run `run_id` in-then-done view fixtures (flipping after `flip` views)."""
        self.write_state(
            f"run_{run_id}_inprogress.json",
            json.dumps({"url": f"https://example/runs/{run_id}", "status": "in_progress", "conclusion": None}),
        )
        self.write_state(
            f"run_{run_id}_done.json",
            json.dumps({"url": f"https://example/runs/{run_id}", "status": "completed", "conclusion": "success"}),
        )
        self.write_state(f"run_{run_id}_flip", str(flip))

    def write_pull_state_sequence(self, pr: int, flip: int, stale: str, final: str) -> None:
        """Give pull `pr` a per-call state sequence: `stale` for reads 1..`flip`,
        `final` thereafter (the `run_<id>_flip`/`run_<id>_views` mechanics for
        PR-state reads; an empty `stale` reproduces the incident's empty read)."""
        self.write_state(f"pull_{pr}_flip", str(flip))
        self.write_state(f"pull_{pr}_stale", stale)
        self.write_state(f"pull_{pr}_final", final)

    def write_close_failure(self, rc: int = 1, msg: str = "") -> None:
        """Record a failing `gh pr close` (exit code `rc`, optional `msg` on stderr)."""
        self.write_state("close_rc", str(rc))
        if msg:
            self.write_state("close_msg", msg)

    def test_sourcing_does_not_run_main(self) -> None:
        """Sourcing the file must not dispatch `main` (BASH_SOURCE guard)."""
        result = self.run_release("true")

        self.assertEqual(result.returncode, 0)

    def test_latest_dev_run_tsv_skips_graph_update_run(self) -> None:
        """`latest_dev_run_tsv` must return the Lint and Test run even when a
        completed Graph Update run at the same SHA is listed first."""
        repo, sha = self.make_repo()
        runs = [self.graph_update_run(sha), self.lint_test_run(sha, status="completed", conclusion="success")]
        self.write_state("run_list.json", json.dumps(runs))

        result = self.run_release("latest_dev_run_tsv", git_repo=repo)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), [f"100\t{sha}\tcompleted\tsuccess"])

    def test_wait_for_dev_ci_never_polls_the_graph_update_run(self) -> None:
        """`wait_for_dev_ci` must wait on the Lint and Test run only; the
        (also present, also green) Graph Update run must never be queried."""
        repo, sha = self.make_repo()
        runs = [self.graph_update_run(sha), self.lint_test_run(sha)]
        self.write_state("run_list.json", json.dumps(runs))
        self.write_run_fixtures(100)
        self.write_run_fixtures(999)

        result = self.run_release("wait_for_dev_ci", git_repo=repo)

        self.assertEqual(result.returncode, 0)
        self.assertIn("success", result.stdout)
        self.assertFalse((self.state / "run_999_views").exists())

    def test_wait_for_pr_checks_polls_pending_then_green(self) -> None:
        """rc=1 with only pending lines must poll (not die); rc=0 must finish."""
        pending = "build (3.11)\tpending\t0\thttps://example/job/1\nCodeQL\tpass\t1s\thttps://example/job/2\n"
        green = "build (3.11)\tpass\t5m\thttps://example/job/1\n"
        self.write_state("pr_checks_1.out", pending)
        self.write_state("pr_checks_1.rc", "1")
        self.write_state("pr_checks_2.out", green)
        self.write_state("pr_checks_2.rc", "0")
        self.write_state("pr_checks_last.out", green)
        self.write_state("pr_checks_last.rc", "0")

        result = self.run_release("wait_for_pr_checks 123")

        self.assertEqual(result.returncode, 0)
        self.assertIn("pending (poll 1/40)", result.stdout)
        self.assertIn("all green", result.stdout)

    def test_wait_for_pr_checks_dies_on_failing_check(self) -> None:
        """rc=1 with a failing line must die with the output on stderr."""
        out = "build (3.11)\tfail\t5m\thttps://example/job/1\nCodeQL\tpass\t1s\thttps://example/job/2\n"
        self.write_state("pr_checks_1.out", out)
        self.write_state("pr_checks_1.rc", "1")
        self.write_state("pr_checks_last.out", out)
        self.write_state("pr_checks_last.rc", "1")

        result = self.run_release("wait_for_pr_checks 123")

        self.assertEqual(result.returncode, 1)
        self.assertIn("checks are failing", result.stderr)
        self.assertIn("build (3.11)", result.stderr)

    def test_close_pr_if_open_skips_merged_pr(self) -> None:
        """An already-merged PR (the v0.35.0 case) must not be `gh pr close`d."""
        self.write_state("pull_456_state", "merged")

        result = self.run_release("close_pr_if_open 456")

        self.assertEqual(result.returncode, 0)
        self.assertIn("already merged", result.stdout)
        self.assertNotIn("pr close", (self.state / "gh_calls.log").read_text())

    def test_close_pr_if_open_closes_open_pr(self) -> None:
        """An open PR must still be closed (the retry budget is pinned to one
        attempt so the test does not sleep under the script's defaults)."""
        self.write_state("pull_456_state", "open")

        result = self.run_release("PR_STATE_RETRY_ATTEMPTS=1; PR_STATE_RETRY_INTERVAL=0; close_pr_if_open 456")

        self.assertEqual(result.returncode, 0)
        self.assertIn("pr close 456", (self.state / "gh_calls.log").read_text())

    def test_close_pr_if_open_never_sleeps_after_last_attempt(self) -> None:
        """The retry loop sleeps only BETWEEN attempts: ATTEMPTS-1 sleeps,
        never after the last one (pinned through a logged fake `sleep`)."""
        self.write_state("pull_456_state", "open")
        sleep_shim = self.shim_dir / "sleep"
        sleep_shim.write_text(
            "#!/usr/bin/env bash\n"
            'S="${RELEASE_TEST_STATE:?RELEASE_TEST_STATE must be set by the test}"\n'
            'printf \'%s\\n\' "$*" >>"$S/sleep.log"\n'
            "exit 0\n"
        )
        os.chmod(sleep_shim, 0o755)

        result = self.run_release("PR_STATE_RETRY_ATTEMPTS=3; PR_STATE_RETRY_INTERVAL=7; close_pr_if_open 456")

        self.assertEqual(result.returncode, 0)
        self.assertIn("pr close 456", (self.state / "gh_calls.log").read_text())
        self.assertEqual((self.state / "sleep.log").read_text().splitlines(), ["7", "7"])

    def test_close_pr_if_open_stale_flips_to_merged_skips_close(self) -> None:
        """A stale/empty state read that flips to merged within the retry budget
        must skip the close entirely (the v0.36.0 race, issue #213)."""
        self.write_pull_state_sequence(456, flip=2, stale="", final="merged")

        result = self.run_release("PR_STATE_RETRY_ATTEMPTS=5; PR_STATE_RETRY_INTERVAL=0; close_pr_if_open 456")

        gh_calls = (self.state / "gh_calls.log").read_text()
        self.assertEqual(result.returncode, 0)
        self.assertIn("already merged", result.stdout)
        self.assertIn("state read: '<empty>' (attempt 1/5)", result.stdout)
        self.assertNotIn("pr close", gh_calls)
        self.assertEqual(sum("pulls/456" in line for line in gh_calls.splitlines()), 3)

    def test_close_pr_if_open_never_merged_close_fails_dies(self) -> None:
        """A state that never flips to merged plus a failing `gh pr close`
        must die with the actionable message naming the PR."""
        self.write_state("pull_456_state", "open")
        self.write_close_failure(msg="ERROR:  could not close the pull request (already merged)")

        result = self.run_release(
            "PR_STATE_RETRY_ATTEMPTS=2; PR_STATE_RETRY_INTERVAL=0; PR_STATE_REVERIFY_ATTEMPTS=3; close_pr_if_open 456"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("pr close 456", (self.state / "gh_calls.log").read_text())
        self.assertIn("PR #456 could not be closed", result.stderr)
        self.assertIn("state re-read is 'open'", result.stderr)
        self.assertIn("resume from the failed stage", result.stderr)
        self.assertIn("could not close the pull request (already merged)", result.stderr)

    def test_close_pr_if_open_close_fails_reverify_merged(self) -> None:
        """A failing `gh pr close` whose re-verify read is merged is the known
        async-merge race: success with the info note (issue #213)."""
        self.write_pull_state_sequence(456, flip=2, stale="open", final="merged")
        self.write_close_failure(msg="ERROR:  could not close the pull request (already merged)")

        result = self.run_release(
            "PR_STATE_RETRY_ATTEMPTS=2; PR_STATE_RETRY_INTERVAL=0; PR_STATE_REVERIFY_ATTEMPTS=3; close_pr_if_open 456"
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("pr close 456", (self.state / "gh_calls.log").read_text())
        self.assertIn("state re-read is merged", result.stdout)
        self.assertIn("known race (issue #213)", result.stdout)

    def test_close_pr_if_open_close_fails_reverify_flips_on_later_read(self) -> None:
        """A failing `gh pr close` whose state flips to merged only on a LATER
        re-verify read still succeeds (the bounded re-verify budget, issue #213)."""
        self.write_pull_state_sequence(456, flip=3, stale="open", final="merged")
        self.write_close_failure(msg="ERROR:  could not close the pull request (already merged)")

        result = self.run_release(
            "PR_STATE_RETRY_ATTEMPTS=1; PR_STATE_RETRY_INTERVAL=0; PR_STATE_REVERIFY_ATTEMPTS=3; close_pr_if_open 456"
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("pr close 456", (self.state / "gh_calls.log").read_text())
        self.assertIn("state re-read is merged", result.stdout)
        self.assertIn("known race (issue #213)", result.stdout)

    def test_close_pr_if_open_guard_rejects_empty_interval(self) -> None:
        """An empty retry variable dies with the actionable guard message
        before any state read or sleep runs (issue #213 hardening)."""
        self.write_state("pull_456_state", "open")

        result = self.run_release("PR_STATE_RETRY_INTERVAL=; close_pr_if_open 456")

        self.assertEqual(result.returncode, 1)
        self.assertIn("release: ERROR:", result.stderr)
        self.assertIn("PR_STATE_RETRY_INTERVAL", result.stderr)

    def test_help_prints_full_usage(self) -> None:
        """`help` must exit 2 and print the complete usage (incl. the final
        keyword line the old `sed -n '2,38p'` range truncated)."""
        result = subprocess.run(["bash", str(RELEASE_SH), "help"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 2)
        self.assertIn("full resolved version.", result.stdout)


class ReleaseShReleaseNotesTestCase(ReleaseShGateTestCase):
    """Tests for `release.sh`'s release-notes stage (the 2026-10-22 revert of
    the release-name behaviour: the notes are PATCHed only, the release name
    is never sent or compared)."""

    def _notes_repo(self, body: str, name: str = "v0.9.9") -> Path:
        """A fixture repo whose CHANGELOG.md carries a dated 0.9.9 section;
        seed the fake release with `body`/`name` and two assets."""
        repo, _ = self.make_repo()
        (repo / "CHANGELOG.md").write_text(
            "# Changelog\n"
            "\n"
            "## [Unreleased]\n"
            "\n"
            "### Added\n"
            "\n"
            "- a later change\n"
            "\n"
            "## [0.9.9] - 2026-01-01\n"
            "\n"
            "### Added\n"
            "\n"
            "- a change\n"
        )
        _git(["add", "."], repo)
        _git(["-c", "user.email=test@test", "-c", "user.name=test", "commit", "-m", "c2"], repo)
        self.write_state(
            "release.json",
            json.dumps(
                {
                    "id": 123,
                    "html_url": "https://example.com/release",
                    "name": name,
                    "body": body,
                    "assets": [{"name": "pkg.tar.gz"}, {"name": "pkg.whl"}],
                }
            ),
        )
        return repo

    def _patch_calls(self) -> list[str]:
        """The logged `gh api --method PATCH` calls (empty when none happened)."""
        if not (self.state / "gh_calls.log").exists():
            return []
        return [line for line in (self.state / "gh_calls.log").read_text().splitlines() if "--method PATCH" in line]

    def test_release_notes_patches_body_only(self) -> None:
        """A not-yet-set body triggers exactly one PATCH carrying `body=@` and
        never a `name=` field."""
        repo = self._notes_repo(body="")
        result = self.run_release("stage_release_notes 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("release v0.9.9 complete", result.stdout)
        calls = self._patch_calls()
        self.assertEqual(len(calls), 1)
        self.assertIn("body=@", calls[0])
        self.assertNotIn("name=", calls[0])

    def test_release_notes_already_set_ignores_stored_name(self) -> None:
        """A matching stored body means "already set" even when the stored name
        is a decorated `vX.Y.Z - <text>` headline — the name is not part of the
        stage's contract (revert 2026-10-22)."""
        repo = self._notes_repo(body="### Added\n\n- a change", name="v0.9.9 - a headline")
        result = self.run_release("stage_release_notes 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already set — nothing to do", result.stdout)
        self.assertEqual(self._patch_calls(), [])

    def test_release_notes_rejects_second_positional(self) -> None:
        """A name-text positional is no longer accepted: the generic
        second-argument guard dies before any file access."""
        result = subprocess.run(
            ["bash", str(RELEASE_SH), "release-notes", "0.9.9", "some text"],
            capture_output=True,
            text=True,
            env=_clean_git_env(),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("unexpected argument 'some text'", result.stderr)


class ReleaseShCloseoutGateTestCase(ReleaseShGateTestCase):
    """Tests for `release.sh`'s feat closeout gate in `stage_precheck`
    (feat-233): full `precheck` runs over a fixture repo that passes the
    six existing checks (a `main` branch for the fetch + fast-forward
    invariant, a previous-release tag, in-window commits, the green CI-run
    fixture, and a fake `uv` answering `uv lock --check`), with feat
    folders under `.specmgr/feat/` and merged-PR fixtures for the fake
    `gh`'s search endpoints."""

    def setUp(self):
        """Add the fake `uv` shim (answers `uv lock --check` with rc 0)."""
        super().setUp()
        uv = self.shim_dir / "uv"
        uv.write_text("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(uv, 0o755)

    def make_release_repo(
        self, feats: list[tuple[str, str | None]], tag_prev: bool = True
    ) -> tuple[Path, dict[str, str]]:
        """A fixture repo that passes the six existing precheck checks.

        Layout (dev == origin/dev at C; main at A; tag v0.9.8 at A when
        `tag_prev`):

            A (c1) --branch main, --tag v0.9.8 (optional)
            |
            B (c2)
            |
            C (c3)  <- dev == origin/dev, carries the feat folders

        `feats` is a list of (folder id, frontmatter status) pairs; a
        `None` status omits the `status:` line. Returns (repo, shas) with
        shas = {"head": C, "in_window": B, "previous": A or "", "main": A}.
        """
        bare = self.tmp / "origin.git"
        repo = self.tmp / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True, env=_clean_git_env())
        _git(["init"], repo)
        _git(["checkout", "-B", "dev"], repo)
        (repo / "file.txt").write_text("a\n")
        _git(["add", "."], repo)
        _git(["-c", "user.email=test@test", "-c", "user.name=test", "commit", "-m", "c1"], repo)
        sha_a = _git(["rev-parse", "HEAD"], repo)
        if tag_prev:
            _git(["tag", "v0.9.8"], repo)
        _git(["branch", "main", sha_a], repo)
        (repo / "file.txt").write_text("b\n")
        _git(["add", "."], repo)
        _git(["-c", "user.email=test@test", "-c", "user.name=test", "commit", "-m", "c2"], repo)
        sha_b = _git(["rev-parse", "HEAD"], repo)
        (repo / "file.txt").write_text("c\n")
        for feat_id, status in feats:
            folder = repo / ".specmgr" / "feat" / feat_id
            folder.mkdir(parents=True)
            fm = f"id: {feat_id}\n"
            if status is not None:
                fm += f"status: {status}\n"
            fm += "version: 1.0.0\n"
            fm += "created: '2026-01-01T00:00:00.000+02:00'\n"
            fm += "updated: '2026-01-01T00:00:00.000+02:00'\n"
            (folder / "README.md").write_text(f"---\n{fm}---\n\n# Feature: {feat_id}\n")
        _git(["add", "."], repo)
        _git(["-c", "user.email=test@test", "-c", "user.name=test", "commit", "-m", "c3"], repo)
        sha_c = _git(["rev-parse", "HEAD"], repo)
        _git(["remote", "add", "origin", str(bare)], repo)
        _git(["push", "origin", "dev"], repo)
        _git(["push", "origin", "main"], repo)
        return repo, {"head": sha_c, "in_window": sha_b, "previous": sha_a if tag_prev else "", "main": sha_a}

    def pr_fixture(self, number: int, head_ref: str, merged_at: str, merge_sha: str) -> dict[str, object]:
        """One closed-PR fixture object (number/head.ref/merged_at/merge_commit_sha)."""
        return {
            "number": number,
            "head": {"ref": head_ref, "label": f"dfch:{head_ref}"},
            "state": "closed",
            "merged_at": merged_at,
            "merge_commit_sha": merge_sha,
        }

    def write_pulls_closed(self, *prs: dict[str, object]) -> None:
        """Seed the fake `gh`'s pulls_closed.json fixture (the search endpoints)."""
        self.write_state("pulls_closed.json", json.dumps(list(prs)))

    def write_green_ci(self, head_sha: str) -> None:
        """A completed green 'Lint and Test' push run at dev's head SHA."""
        run = self.lint_test_run(head_sha, status="completed", conclusion="success")
        self.write_state("run_list.json", json.dumps([run]))

    def test_precheck_gate_dies_for_review_feat_shipped_in_window(self) -> None:
        """ACC-001: a review-status feat whose merged PR's delivery SHA is
        inside vPrev..HEAD fails the full precheck, naming the feat, its
        status, the PR number, and the delivery sha."""
        repo, shas = self.make_release_repo([("feat-7-closeout-gate", "review")])
        self.write_pulls_closed(self.pr_fixture(42, "feat-7-closeout-gate", "2026-10-01T00:00:00Z", shas["in_window"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("feat closeout gate failed", result.stderr)
        self.assertIn("feat-7-closeout-gate", result.stderr)
        self.assertIn("status is 'review'", result.stderr)
        self.assertIn("PR #42", result.stderr)
        self.assertIn(shas["in_window"], result.stderr)
        self.assertIn("re-run: scripts/release.sh precheck v0.9.9", result.stderr)
        self.assertNotIn("all checks passed", result.stdout)

    def test_precheck_gate_passes_for_done_feat(self) -> None:
        """ACC-002: the same in-window delivery at status: done passes the
        gate and the full precheck."""
        repo, shas = self.make_release_repo([("feat-7-closeout-gate", "done")])
        self.write_pulls_closed(self.pr_fixture(42, "feat-7-closeout-gate", "2026-10-01T00:00:00Z", shas["in_window"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("precheck: all checks passed for v0.9.9", result.stdout)

    def test_precheck_gate_passes_for_plan_only_feat(self) -> None:
        """ACC-002: a plan-only feat (no merged PR for its head ref, and
        none in the page scan) passes at any non-done status (REQ-002)."""
        repo, shas = self.make_release_repo([("feat-8-plan-only", "progress")])
        self.write_pulls_closed()
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("precheck: all checks passed for v0.9.9", result.stdout)

    def test_precheck_gate_passes_for_feat_delivered_before_prev_tag(self) -> None:
        """ACC-003: a review-status feat whose delivery SHA is an ancestor
        of vPrev (shipped in an earlier release) passes the gate (REQ-003)."""
        repo, shas = self.make_release_repo([("feat-9-earlier-release", "review")])
        self.write_pulls_closed(self.pr_fixture(55, "feat-9-earlier-release", "2026-09-01T00:00:00Z", shas["previous"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("precheck: all checks passed for v0.9.9", result.stdout)
        self.assertIn("shipped in an earlier release", result.stdout)

    def test_precheck_gate_dies_for_missing_status(self) -> None:
        """A feat folder whose frontmatter has no `status:` line is a
        violation in its own right — reported before any PR lookup
        (fail-safe: block, never skip; an in-window merged PR exists for
        the ref and must not be looked up or reported)."""
        repo, shas = self.make_release_repo([("feat-10-broken", None)])
        self.write_pulls_closed(self.pr_fixture(77, "feat-10-broken", "2026-10-01T00:00:00Z", shas["in_window"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        gh_calls = (self.state / "gh_calls.log").read_text()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("feat-10-broken", result.stderr)
        self.assertIn("frontmatter 'status:' is missing or unparseable", result.stderr)
        self.assertNotIn("PR #77", result.stderr)
        self.assertNotIn("head={owner}:feat-10-broken", gh_calls)

    def test_precheck_gate_dies_for_out_of_set_status(self) -> None:
        """A `status:` value outside the closed set (planning/progress/
        review/done) is the same frontmatter-defect violation."""
        repo, shas = self.make_release_repo([("feat-11-broken", "wip")])
        self.write_pulls_closed(self.pr_fixture(78, "feat-11-broken", "2026-10-01T00:00:00Z", shas["in_window"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        gh_calls = (self.state / "gh_calls.log").read_text()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("feat-11-broken", result.stderr)
        self.assertIn("frontmatter 'status:' is missing or unparseable", result.stderr)
        self.assertNotIn("PR #78", result.stderr)
        self.assertNotIn("head={owner}:feat-11-broken", gh_calls)

    def test_precheck_gate_prefix_fallback_gates_renamed_branch(self) -> None:
        """ACC-011: a review-status feat whose work merged ONLY under a
        renamed feat-<NNN>-* branch (no merged PR for the exact head ref)
        is still gated via the issue-number-prefix fallback; the one-shot
        page scan is fetched exactly once per run even though two feat
        folders use the fallback, and a second feat with no merged
        delivery stays ungated (REQ-002)."""
        repo, shas = self.make_release_repo(
            [
                ("feat-134-similarity-rename", "review"),
                ("feat-144-ref-artifact", "review"),
            ]
        )
        self.write_pulls_closed(
            self.pr_fixture(168, "feat-134-similarity-requires-mcp", "2026-09-29T11:47:00Z", shas["in_window"]),
        )
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        gh_calls = (self.state / "gh_calls.log").read_text()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("feat-134-similarity-rename", result.stderr)
        self.assertIn("PR #168", result.stderr)
        self.assertIn(shas["in_window"], result.stderr)
        self.assertNotIn("feat-144-ref-artifact", result.stderr)
        self.assertIn("head={owner}:feat-134-similarity-rename", gh_calls)
        self.assertIn("head={owner}:feat-144-ref-artifact", gh_calls)
        scan_calls = [line for line in gh_calls.splitlines() if "pulls?state=closed&per_page=100" in line]
        self.assertEqual(len(scan_calls), 1)

    def test_precheck_gate_newest_delivery_wins_across_exact_and_fallback(self) -> None:
        """The delivery is the newest by merged_at ACROSS the exact head-ref
        match and the prefix fallback (design decision: a folder that
        shipped from both a folder-named branch (PR #137) and a renamed
        feat-<NNN>-* branch (PR #168) is gated on #168, not #137)."""
        repo, shas = self.make_release_repo([("feat-134-related-artifact-similarity", "review")])
        self.write_pulls_closed(
            self.pr_fixture(137, "feat-134-related-artifact-similarity", "2026-09-29T08:47:07Z", shas["in_window"]),
            self.pr_fixture(168, "feat-134-similarity-requires-mcp", "2026-09-29T11:47:00Z", shas["head"]),
        )
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("feat-134-related-artifact-similarity", result.stderr)
        self.assertIn("PR #168", result.stderr)
        self.assertIn(shas["head"], result.stderr)
        self.assertNotIn("PR #137", result.stderr)

    def test_precheck_gate_no_prior_tag_window_is_head(self) -> None:
        """With no prior release tag the window is HEAD: a review-status
        feat with a merged delivery counts as in-window and the precheck
        dies (the first-release case, with the no-tag info note)."""
        repo, shas = self.make_release_repo([("feat-15-first-release", "review")], tag_prev=False)
        self.write_pulls_closed(self.pr_fixture(66, "feat-15-first-release", "2026-08-01T00:00:00Z", shas["in_window"]))
        self.write_green_ci(shas["head"])

        result = self.run_release("stage_precheck 0.9.9", git_repo=repo)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no release tag reachable from HEAD", result.stdout)
        self.assertIn("feat-15-first-release", result.stderr)
        self.assertIn("PR #66", result.stderr)
        self.assertIn(shas["in_window"], result.stderr)
