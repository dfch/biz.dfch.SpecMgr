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

"""Permanent repo-tree pin of the sharded document layout (feat-245 Phase 180, Task 180.240, I1).

Every tracked file under ``docs/<d>/`` of the thirteen sharded UUID domains must be
``docs/<d>/<lang>/<2-hex>/<uuid>-<slug>.md`` with the shard equal to ``id[:2]`` and the
file-name uuid equal to the frontmatter ``id`` -- ACC-006 continuously enforced. The
``specmgr lint`` sweep cannot catch a flat file (it reads shard dirs only), and the
change-scoped lint gate only sees changed paths, so a flat document merged from another
branch (the #268 QA transcript, moved in merge 467d53b6) would otherwise stay invisible.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

import yaml

from biz.dfch.specmgr.general.tools._domains import UUID_DOMAINS

#: The repository root (this file lives at ``tests/test_repo_doc_layout.py``).
_REPO_ROOT = Path(__file__).resolve().parents[1]

_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def _tracked_files(rel_dir: str) -> list[str]:
    """The ``git ls-files`` listing of ``rel_dir`` (repo-relative, POSIX separators)."""
    completed = subprocess.run(
        ["git", "ls-files", "--", rel_dir],
        cwd=_REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = [line for line in completed.stdout.splitlines() if line.strip()]
    return result


def _frontmatter_id(path: Path) -> str | None:
    """The frontmatter ``id`` of a tracked document (``None`` when absent)."""
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    frontmatter = yaml.safe_load(text.split("\n---\n", 1)[0].removeprefix("---\n"))
    result = frontmatter.get("id") if isinstance(frontmatter, dict) else None
    return None if result is None else str(result)


@unittest.skipUnless(shutil.which("git") and (_REPO_ROOT / ".git").exists(), "needs a git checkout")
class TestRepoDocLayout(unittest.TestCase):
    """ACC-006 as a permanent pin over the real tracked tree."""

    def test_every_tracked_sharded_domain_file_has_the_sharded_shape(self):
        total = 0
        for domain in UUID_DOMAINS:
            pattern = re.compile(rf"^docs/{domain}/[a-z]{{2}}/(?P<shard>[0-9a-f]{{2}})/(?P<id>{_UUID})-[^/]+\.md$")
            for rel in _tracked_files(f"docs/{domain}/"):
                total += 1
                with self.subTest(path=rel):
                    match = pattern.fullmatch(rel)
                    self.assertIsNotNone(match, f"{rel} is not docs/{domain}/<lang>/<2-hex>/<uuid>-<slug>.md")
                    assert match is not None
                    self.assertEqual(match.group("shard"), match.group("id")[:2], rel)
                    self.assertEqual(_frontmatter_id(_REPO_ROOT / rel), match.group("id"), rel)
        self.assertGreater(total, 0, "the repo must track at least one sharded document")


if __name__ == "__main__":
    unittest.main()
