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

"""Bidirectional drift guard between `server.json`'s `environmentVariables` and the
`SPECMGR_*` environment variables the code actually reads in `src/`
(feat-126-server-json-env-drift, GitHub issue #126).

`server.json` is the hand-maintained MCP registry manifest; it has already drifted once
(`SPECMGR_SIMILARITY_DISABLED`/`SPECMGR_FEAT_WARMUP_DISABLED` were missing, and the three
`SPECMGR_MCP_*` entries were stale). This test makes the source the single source of
truth: it scans `src/**/*.py` for environment-variable read sites -- the four syntactic
shapes of the plan's Design Notes (string-literal assignment, `getenv` call, `environ`
access, Typer `envvar=` option) -- and asserts set equality in both directions, with
failure messages naming the specific missing (read in `src/`, absent from the manifest)
and extra (in the manifest, never read in `src/`) entries. It additionally pins the
manifest's structural invariants (REQ-002): unique `name`s, non-empty `description`s,
and `default` present on an entry iff the code reads that variable with a default.

The scan is a regex over source text with `#` comments and triple-quoted (docstring)
regions blanked -- not a full parser (the plan pins the line-regex design, with
tightening as the sanctioned remedy for false positives; this blanking is that
tightening, pinned by the negative fixtures below). A single-line string whose content
quotes one of the shapes verbatim is a known accepted limitation (no such line exists
in the corpus, and one would fail visibly, naming the entry, if introduced). The
default-presence classifier is line-anchored where it needs line context, for the same
reason: only an explicit second argument, a statement line whose entire code is
`<identifier> = get(NEEDLE)` (the corpus's assignment read, the caller applying the
fallback), or the central env-var registry's own `get_with_default(NEEDLE)` accessor
call (the post-migration corpus read shape, feat-208 Phase 120 -- the accessor itself
inserts the registered default) counts as a read with a default; a plain get in any
other context -- a `return`, an `if` condition, or the registry's raw `get(NEEDLE)`
presence accessor, which is a presence read and is pinned as such -- counts as no
default.

The scanner machinery described above (the shape patterns, the blanking, the
eight-pattern default-presence classifier, the Typer `Annotated` option-default scan)
lives in the shared `tests/_env_scan.py` helper (extracted by feat-208 Phase 150, Task
150.100, behaviour-preserving -- this file's assertions run on it unchanged, on the
default `SPECMGR_` name pattern); this file keeps the manifest-side logic and the
scan's negative fixtures.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tests._env_scan import REPO_ROOT, env_var_code_defaults, scan_env_var_read_sites

#: The hand-maintained manifest this test guards.
SERVER_JSON = REPO_ROOT / "server.json"


def _load_manifest_env_vars(path: Path) -> list[dict[str, object]]:
    """The `environmentVariables` entries of the manifest's first (and only) package.

    Args:
        path: The `server.json` manifest path.

    Returns:
        The raw entry dicts, each carrying at least `name` (and, per REQ-002,
        `description`).

    Raises:
        FileNotFoundError: When `path` does not exist.
        json.JSONDecodeError: When the manifest is not valid JSON.
        AssertionError/KeyError/TypeError: When the manifest lacks the expected
            `packages`/`environmentVariables` shape -- a malformed manifest must fail
            the guard loudly, never parse silently.
    """
    assert path.is_file(), path
    manifest = json.loads(path.read_text(encoding="utf-8"))
    packages = manifest["packages"]
    assert isinstance(packages, list) and packages, "server.json must carry at least one package"
    environment_variables = packages[0]["environmentVariables"]
    assert isinstance(environment_variables, list), "environmentVariables must be a list"
    result: list[dict[str, object]] = environment_variables
    return result


class TestServerJsonDrift(unittest.TestCase):
    """Bidirectional drift between the `src/` read sites and `server.json` (ACC-002/ACC-003)."""

    def setUp(self) -> None:
        self.sites = scan_env_var_read_sites()
        self.source_names: set[str] = set(self.sites)
        self.manifest_entries = _load_manifest_env_vars(SERVER_JSON)
        self.manifest_names: set[str] = set()
        for entry in self.manifest_entries:
            name = entry.get("name")
            if isinstance(name, str):
                self.manifest_names.add(name)
        self.code_defaults = env_var_code_defaults()

    def test_source_names_match_manifest_names_bidirectionally(self) -> None:
        """Every name read in `src/` is in the manifest, and every manifest name is read in `src/`."""
        missing_from_manifest = sorted(self.source_names - self.manifest_names)
        extra_in_manifest = sorted(self.manifest_names - self.source_names)
        message = (
            "server.json's environmentVariables drifted from the SPECMGR_* read sites in src/ "
            "(feat-126-server-json-env-drift, issue #126): "
            f"read in src/ but missing from the manifest: {missing_from_manifest}; "
            f"listed in the manifest but never read in src/: {extra_in_manifest}"
        )
        self.assertEqual(sorted(self.manifest_names), sorted(self.source_names), message)

    def test_manifest_names_are_unique(self) -> None:
        """REQ-002: the manifest's `name`s are unique, and every entry carries a usable name."""
        names: list[str] = []
        malformed: list[str] = []
        for entry in self.manifest_entries:
            name = entry.get("name")
            if not isinstance(name, str) or not name.strip():
                malformed.append(repr(entry))
                continue
            names.append(name)
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        self.assertEqual([], malformed, f"environmentVariable entries without a usable name: {malformed}")
        self.assertEqual([], duplicates, f"duplicate environmentVariable names in server.json: {duplicates}")

    def test_manifest_descriptions_are_non_empty(self) -> None:
        """REQ-002: every manifest entry carries a non-empty `description`."""
        offenders: list[str] = []
        for entry in self.manifest_entries:
            description = entry.get("description")
            if not isinstance(description, str) or not description.strip():
                offenders.append(str(entry.get("name", "<no name>")))
        self.assertEqual([], offenders, f"environmentVariable entries with a missing or empty description: {offenders}")

    def test_default_present_iff_code_has_default(self) -> None:
        """REQ-002: `default` is present on an entry iff the code reads the variable with a default."""
        drift: list[str] = []
        for entry in self.manifest_entries:
            name = entry.get("name")
            if not isinstance(name, str):
                continue
            manifest_has_default = "default" in entry
            code_has_default = self.code_defaults.get(name, False)
            if manifest_has_default != code_has_default:
                drift.append(
                    f"{name} (manifest default: {manifest_has_default}, code-side default: {code_has_default})"
                )
        self.assertEqual(
            [],
            drift,
            "default presence drifted between server.json and the code-side read classification: " + "; ".join(drift),
        )

    def test_bare_speccmgr_root_identifier_is_not_reported(self) -> None:
        """ACC-004: the `_SPECMGR_ROOT` identifier in `src/biz/dfch/specmgr/_paths.py` is not an
        environment variable."""
        self.assertNotIn(
            "SPECMGR_ROOT",
            self.source_names,
            "the scan reported SPECMGR_ROOT -- the _SPECMGR_ROOT identifier (which merely contains the "
            "prefix, as does REPO_ROOT = _SPECMGR_ROOT.parent...) must not be reported",
        )


class TestScanNegativeFixtures(unittest.TestCase):
    """Synthetic fixture trees pinning the scan's false-positive guards (ACC-004)."""

    def setUp(self) -> None:
        self.tmp: Path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _write_module(self, name: str, source: str) -> Path:
        """Write one module under the fixture's own `src/` tree and return its path.

        Args:
            name: The module file name (e.g. `fake_mod.py`).
            source: The module's raw source text.

        Returns:
            The written file's path.
        """
        module_dir = self.tmp / "src" / "fakepkg"
        module_dir.mkdir(parents=True, exist_ok=True)
        module_path = module_dir / name
        module_path.write_text(source, encoding="utf-8")
        return module_path

    def test_docstring_prose_and_comment_mentions_are_not_reported(self) -> None:
        """Docstring prose (the corpus' backtick style) and comment mentions are not read sites."""
        source = (
            '"""A module docstring mentioning names in prose.\n'
            "\n"
            "It names ``SPECMGR_FAKE_DOCSTRING_VAR`` the way the corpus docstrings do,\n"
            "without quoting one of the read-site shapes.\n"
            '"""\n'
            "\n"
            "# A comment line mentioning SPECMGR_FAKE_COMMENT_VAR.\n"
            "\n"
            "import os\n"
            "\n"
            'FAKE_ENV_VAR = "SPECMGR_FAKE_REAL"\n'
            "\n"
            "\n"
            "def read_fake() -> str | None:\n"
            '    """A function docstring mentioning SPECMGR_FAKE_FUNC_DOC_VAR."""\n'
            "    value = os.environ.get(FAKE_ENV_VAR)\n"
            "    return value\n"
        )
        self._write_module("fake_mod.py", source)

        sut = scan_env_var_read_sites(self.tmp)
        defaults = env_var_code_defaults(self.tmp)

        self.assertEqual(
            {"SPECMGR_FAKE_REAL"},
            set(sut),
            "docstring-prose and comment mentions must not be reported as read sites",
        )
        self.assertEqual({"SPECMGR_FAKE_REAL": True}, defaults)

    def test_docstring_and_comment_quoting_full_shapes_are_not_reported(self) -> None:
        """A docstring or comment line containing one of the shapes verbatim is not a read site."""
        source = (
            '"""A docstring quoting read-site shapes verbatim:\n'
            "\n"
            'QUOTED_DOC_CONST = "SPECMGR_FAKE_DOC_ASSIGNED"\n'
            "and envvar='SPECMGR_FAKE_DOC_TYPER', neither of which is real code.\n"
            '"""\n'
            "\n"
            '# LEGACY_DOC_CONST = "SPECMGR_FAKE_COMMENT_ASSIGN"  # a commented-out assignment\n'
            "\n"
            "import os\n"
            "\n"
            'REAL_ENV_VAR = "SPECMGR_FAKE_REAL"\n'
            "\n"
            "\n"
            "def read_real() -> str | None:\n"
            "    value = os.getenv(REAL_ENV_VAR)\n"
            "    return value\n"
        )
        self._write_module("fake_mod.py", source)

        sut = scan_env_var_read_sites(self.tmp)
        defaults = env_var_code_defaults(self.tmp)

        self.assertEqual(
            {"SPECMGR_FAKE_REAL"},
            set(sut),
            "a docstring or comment quoting an assignment or a Typer envvar option must not be reported",
        )
        self.assertEqual({"SPECMGR_FAKE_REAL": True}, defaults)


if __name__ == "__main__":
    unittest.main()
