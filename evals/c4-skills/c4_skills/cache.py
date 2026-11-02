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

"""The result cache for the `none` and `upstream` conditions (Task 100.130).

Those conditions are content-pinned (no skill iteration between runs), so a
rerun under the same (case, condition, version tuple, grader hash) is the
same measurement: the cached trial summaries are reused and the trials are
not re-run. The `skill` condition is never cached (each variant is a new
measurement by its content hash).

The cache lives in the gitignored `evals/c4-skills/cache/` directory, one
JSON file per (case, condition).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import pins

#: The cache subdirectory (gitignored) under the harness root.
CACHE_DIRNAME = "cache"


@dataclass(frozen=True)
class CacheKey:
    """One cache entry: everything that must match for a hit.

    Attributes:
        case_id: The case id.
        condition: The condition (`none`/`upstream`).
        version_tuple_hash: The pins' stable hash.
        grader_hash: The graders + case source hash.
        skill_variant_hash: The condition's skill content hash.
    """

    case_id: str
    condition: str
    version_tuple_hash: str
    grader_hash: str
    skill_variant_hash: str

    def as_dict(self) -> dict:
        """Return the JSON-serialisable key."""
        result = {
            "case_id": self.case_id,
            "condition": self.condition,
            "version_tuple_hash": self.version_tuple_hash,
            "grader_hash": self.grader_hash,
            "skill_variant_hash": self.skill_variant_hash,
        }
        return result

    @classmethod
    def make(cls, case_id: str, condition: str, grader_hash: str, skill_variant_hash: str) -> "CacheKey":
        """Build a key with the current pins' version-tuple hash."""
        assert condition in pins.CACHEABLE_CONDITIONS, f"condition {condition!r} is not cacheable"
        result = cls(
            case_id=case_id,
            condition=condition,
            version_tuple_hash=pins.version_tuple_hash(),
            grader_hash=grader_hash,
            skill_variant_hash=skill_variant_hash,
        )
        return result


class ResultCache:
    """The on-disk result cache (one JSON file per case/condition)."""

    def __init__(self, cache_root: Path) -> None:
        """Initialize over `cache_root` (created on first store).

        Args:
            cache_root: The gitignored cache directory.
        """
        assert isinstance(cache_root, Path)
        self.root = cache_root

    def _path(self, case_id: str, condition: str) -> Path:
        """Return the cache file path for one (case, condition)."""
        assert isinstance(case_id, str) and case_id
        assert isinstance(condition, str) and condition
        safe_condition = condition.replace("/", "-")
        result = self.root / f"{case_id}.{safe_condition}.json"
        return result

    def get(self, key: CacheKey) -> dict | None:
        """Return the cached entry for `key`, or None on any mismatch.

        The stored entry must carry the same key (version tuple, grader,
        skill variant) or it is a miss.
        """
        path = self._path(key.case_id, key.condition)
        if not path.is_file():
            return None
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if not isinstance(stored, dict) or stored.get("key") != key.as_dict():
            return None
        result: dict | None = stored
        return result

    def put(self, key: CacheKey, trials: list[dict]) -> None:
        """Store one (case, condition)'s trial summaries under `key`.

        Args:
            key: The cache key (recorded inside the entry).
            trials: The per-trial summary dicts (the runner's records).
        """
        assert isinstance(trials, list)
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(key.case_id, key.condition)
        payload = json.dumps({"key": key.as_dict(), "trials": trials}, indent=2, sort_keys=True) + "\n"
        path.write_text(payload, encoding="utf-8")
