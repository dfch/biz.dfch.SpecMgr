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

"""The `upstream` skill fetch (Task 100.110/120).

The upstream skills (`jrjsmrtn/c4-skills`) are fetched on the host at run
time from the pinned commit SHA and mounted into the trial container.
Nothing is vendored into this repository: the fetch lands in the
gitignored `evals/c4-skills/.upstream/` cache dir and is verified (exact
SHA, expected skill folders) before use. Upstream is never patched.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import pins

#: The cache subdirectory (gitignored) that holds the fetched upstream
#: checkout.
UPSTREAM_CACHE_DIRNAME = ".upstream"

#: The file that records the checked-out SHA (a stale cache with a
#: different SHA is refetched).
SHA_MARKER_NAME = ".pinned-sha"


@dataclass(frozen=True)
class UpstreamSource:
    """A verified upstream checkout.

    Attributes:
        root: The checkout directory (the repo at the pinned SHA).
        sha: The verified commit SHA.
        skills: The skill directory names found under `root/skills`.
        files: Every skill file as (path relative to the skills root,
            bytes), for the variant content hash.
    """

    root: Path
    sha: str
    skills: tuple[str, ...]
    files: list[tuple[str, bytes]]


def _run_git(args: list[str], cwd: Path | None = None, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    """Run one git command (fixed pinned remote; no user input)."""
    result = subprocess.run(  # noqa: S603 -- fixed pinned remote
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


def ensure_upstream(cache_root: Path, sha: str | None = None) -> UpstreamSource:
    """Fetch (or reuse) the upstream checkout at the pinned SHA.

    Args:
        cache_root: The gitignored cache directory (created if missing).
        sha: The commit to check out (defaults to the pinned SHA).

    Returns:
        The verified UpstreamSource.

    Raises:
        RuntimeError: If the fetch/checkout fails, the checked-out SHA
            differs from the requested one, or an expected skill folder is
            missing.
    """
    assert cache_root is not None
    requested = sha or pins.UPSTREAM_SHA_PIN
    assert isinstance(requested, str) and len(requested) == 40

    checkout = cache_root / "jrjsmrtn-c4-skills"
    marker = checkout / SHA_MARKER_NAME
    if marker.is_file() and marker.read_text(encoding="utf-8").strip() == requested and (checkout / ".git").is_dir():
        root = checkout
    else:
        cache_root.mkdir(parents=True, exist_ok=True)
        if checkout.exists():
            subprocess.run(["rm", "-rf", str(checkout)], check=True, timeout=60)  # noqa: S603 -- cache dir only
        proc = _run_git(["clone", "--filter=blob:none", pins.UPSTREAM_REPO_URL, str(checkout)])
        if proc.returncode != 0:
            raise RuntimeError(f"upstream clone failed: {proc.stderr.strip()}")
        proc = _run_git(["checkout", "--detach", requested], cwd=checkout)
        if proc.returncode != 0:
            raise RuntimeError(f"upstream checkout {requested} failed: {proc.stderr.strip()}")
        marker.write_text(requested + "\n", encoding="utf-8")
        root = checkout

    head_proc = _run_git(["rev-parse", "HEAD"], cwd=root)
    actual = head_proc.stdout.strip()
    if actual != requested:
        raise RuntimeError(f"upstream checkout SHA drift: {actual} != {requested}")

    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise RuntimeError("upstream checkout has no skills/ folder")
    skill_dirs = sorted(p.name for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    missing = [name for name in pins.UPSTREAM_SKILLS if name not in skill_dirs]
    if missing:
        raise RuntimeError(f"upstream checkout is missing skill folders: {missing}")

    files: list[tuple[str, bytes]] = []
    for skill in skill_dirs:
        for path in sorted(skills_root.glob(f"{skill}/**/*")):
            if path.is_file():
                rel = path.relative_to(skills_root).as_posix()
                files.append((rel, path.read_bytes()))

    result = UpstreamSource(root=root, sha=actual, skills=tuple(skill_dirs), files=files)
    return result


def mount_skills_into(workdir: Path, source: UpstreamSource) -> list[str]:
    """Copy the upstream skills into a trial work dir's skill location.

    The target is `<workdir>/.opencode/skills/<name>/` (opencode 2.x's
    project skill location, verified against the pinned image). Returns the
    skill names mounted.
    """
    assert workdir.is_dir()
    assert source.skills
    target_root = workdir / ".opencode" / "skills"
    mounted: list[str] = []
    for skill in source.skills:
        src = source.root / "skills" / skill
        dst = target_root / skill
        dst.mkdir(parents=True, exist_ok=True)
        for path in src.rglob("*"):
            if path.is_file():
                rel = path.relative_to(src)
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
        mounted.append(skill)
    result = mounted
    return result
