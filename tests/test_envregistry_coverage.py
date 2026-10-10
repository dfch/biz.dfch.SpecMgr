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

"""Documentation coverage drift guard: the registry vs. the README and the
`server.json` manifest (feat-208, REQ-004, ACC-004).

The feat-208 plan's Design Notes "Documentation tracking" names this as the
second of the two registry-anchored tests (the first is the
registry-to-source completeness test in
`tests/test_envregistry_completeness.py`): every registered environment
variable is documented in the root `README.md`'s "Environment Variables"
section and in `server.json`'s `environmentVariables`, with faithful
`default`/`choices`/`format` (presence-based variables carry no default),
so "is every env var documented?" is a test result, not a manual audit.
The failure messages name the specific variable (and, for the manifest
fidelity checks, the drifted field with both values).

The ACC-002 Typer-default check runs here too (the plan assigns it to this
phase, Task 160.100): the three `specmgr mcp` Typer options
(`SPECMGR_MCP_TRANSPORT`/`SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`) must
source their `default=` values from the registry records' own defaults --
the extracted default expression must be a reference to the module's own
`_envregistry.register(...)` record (`.default`, optionally wrapped in
`int()` for the numeric port option), never a raw literal, and its
evaluated value must equal the registry default. The extraction is the
shared helper's `typer_option_default_expression` (Task 150.100 extended
the Annotated scan to capture the expression text for exactly this
comparison).

Self-contained: the nine owning modules' import-time registrations
(feat-208 Phase 110) are triggered by the explicit side-effect imports
below -- the same module list `tests/test_envregistry_completeness.py`
uses -- so this test is green when run alone. These tests read the
registry; they never register into it. The manifest's one
machine-dependent default (`FASTEMBED_CACHE_PATH`'s
`<tempdir>/fastembed_cache`) is compared with the process's temp-dir
prefix replaced by the literal `<tempdir>` placeholder; for every other
default that normalization is pinned to change nothing, so the
placeholder convention can never leak in silently.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import tempfile
import unittest

import biz.dfch.specmgr.adr.tools._paths  # noqa: F401 (side-effects only: SPECMGR_ADR_DIR registration)
import biz.dfch.specmgr.cli  # noqa: F401 (side-effects only: SPECMGR_TESTS_NO_DOTENV registration)

# The bare import (no `as` alias): `commands/__init__.py`'s own
# `from .mcp import mcp` shadows the submodule name in the parent's
# namespace, so `import ... as x` would bind the function, not the module
# -- the module object is read back from `sys.modules` in
# `TestTyperMcpOptionDefaults.setUp`.
import biz.dfch.specmgr.commands.mcp  # noqa: F401 (side-effects only: the three Typer MCP vars' registration)
import biz.dfch.specmgr.feat.tools._paths  # noqa: F401 (side-effects only: SPECMGR_FEAT_DIR registration)
import biz.dfch.specmgr.general.resources.config  # noqa: F401 (side-effects only: FASTEMBED_CACHE_PATH registration)
import biz.dfch.specmgr.general.tools._doc_paths  # noqa: F401 (side-effects only: SPECMGR_DOCS_DIR registration)
import biz.dfch.specmgr.general.tools._embedding  # noqa: F401 (side-effects only: SPECMGR_SIMILARITY_DISABLED registration)
import biz.dfch.specmgr.general.tools._startup_warmup  # noqa: F401 (side-effects only: SPECMGR_FEAT_WARMUP_DISABLED registration)
import biz.dfch.specmgr.uc.tools.validate_plantuml  # noqa: F401 (side-effects only: the plantuml trio's registration)

from biz.dfch.specmgr import _envregistry
from tests._env_scan import (
    REPO_ROOT,
    SHAPE_TYPER_ENVVAR,
    scan_env_var_read_sites,
    typer_option_default_expression,
)

#: The root `README.md` this test's section extraction runs against.
README_MD = REPO_ROOT / "README.md"
#: The hand-maintained manifest this test's fidelity checks run against.
SERVER_JSON = REPO_ROOT / "server.json"
#: The README section heading every registered variable must be documented in.
README_ENV_SECTION_HEADING = "### Environment Variables"
#: The `specmgr mcp` command module whose Typer options' defaults are checked (ACC-002).
MCP_COMMAND_PATH = REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / "commands" / "mcp.py"
#: The three `specmgr mcp` transport options, one per registered variable.
_MCP_OPTION_VARS = ("SPECMGR_MCP_TRANSPORT", "SPECMGR_MCP_HOST", "SPECMGR_MCP_PORT")
#: The default-expression form the Typer options must take: a reference to the
#: module-level `register(...)` record's own `.default` (optionally wrapped in
#: `int()` for the numeric port option) -- never a raw literal.
_REGISTRY_REF_RE = re.compile(r"^(?:int\()?([A-Za-z_]\w*)\.default(?:\))?$")
#: The manifest's placeholder for the one machine-dependent default
#: (`FASTEMBED_CACHE_PATH`'s temp-dir-prefixed fallback).
_TEMPDIR_PLACEHOLDER = "<tempdir>"
#: The only registered default that is machine-dependent (the process's
#: temp-dir prefix), so the only one the manifest documents with the
#: `<tempdir>` placeholder; every other default is a literal string that must
#: match exactly (no normalization applied to it).
_TEMPDIR_PLACEHOLDER_VARS = frozenset({"FASTEMBED_CACHE_PATH"})
#: A markdown ATX heading of any level (for the section terminator scan).
_HEADING_RE = re.compile(r"^(#{1,6})\s")


def _extract_markdown_section(text: str, heading: str) -> str:
    """The body of one exact-text markdown section, extracted structurally.

    From the `heading` line (matched by its stripped, exact text) to -- not
    including -- the next ATX heading of the same or higher level (a heading
    with the same or fewer `#` characters); the end of the file when there is
    none. The terminator is found, never hardcoded, so the section's current
    end heading (today `### Semantic Similarity Search`) may move.

    Args:
        text: The markdown file's full text.
        heading: The section heading's exact text (e.g.
            `### Environment Variables`).

    Returns:
        The section body (the lines between the heading line and the
        terminating heading, joined; the heading line itself excluded).

    Raises:
        AssertionError: When `heading` is not found in `text`.
    """
    lines = text.split("\n")
    start = next((index for index, line in enumerate(lines) if line.strip() == heading), None)
    assert start is not None, f"markdown heading {heading!r} not found"
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = _HEADING_RE.match(lines[index])
        if match is not None and len(match.group(1)) <= level:
            end = index
            break
    result = "\n".join(lines[start + 1 : end])
    return result


def _manifest_env_vars() -> dict[str, dict[str, object]]:
    """`server.json`'s `packages[0].environmentVariables` entries, keyed by `name`.

    Args:
        None.

    Returns:
        The raw entry dicts keyed by their `name` field (a duplicate `name`
        keeps its last occurrence -- feat-126's own
        `test_manifest_names_are_unique` pins the no-duplicates invariant).

    Raises:
        AssertionError: When the manifest is missing, not valid JSON, or lacks
            the expected `packages`/`environmentVariables` shape -- a malformed
            manifest must fail the guard loudly, never parse silently.
    """
    assert SERVER_JSON.is_file(), SERVER_JSON
    manifest = json.loads(SERVER_JSON.read_text(encoding="utf-8"))
    packages = manifest["packages"]
    assert isinstance(packages, list) and packages, "server.json must carry at least one package"
    environment_variables = packages[0]["environmentVariables"]
    assert isinstance(environment_variables, list), "environmentVariables must be a list"
    result: dict[str, dict[str, object]] = {}
    for entry in environment_variables:
        assert isinstance(entry, dict), entry
        name = entry.get("name")
        assert isinstance(name, str) and name, entry
        result[name] = entry
    return result


def _registered_record_binding(tree: ast.Module, var: str) -> str | None:
    """The module-level identifier `commands/mcp.py` binds the var's `register(...)` record to.

    The top-level assignment whose value is an `_envregistry.register(...)`
    call whose first positional argument is the var's name literal (the
    Phase 110 registration form).

    Args:
        tree: The parsed `commands/mcp.py` module.
        var: The environment-variable name to look up.

    Returns:
        The bound identifier (e.g. `_mcp_transport_var`), or `None` when no
        such binding exists in the module.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        call = node.value
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            continue
        if call.func.attr != "register":
            continue
        if not isinstance(call.func.value, ast.Name) or call.func.value.id != "_envregistry":
            continue
        if not call.args or not isinstance(call.args[0], ast.Constant) or call.args[0].value != var:
            continue
        result = target.id
        return result
    result = None
    return result


class TestReadmeEnvironmentVariablesCoverage(unittest.TestCase):
    """REQ-004/ACC-004: every registered variable is named in the README's "Environment Variables" section."""

    def setUp(self) -> None:
        self.records: dict[str, _envregistry.EnvVar] = {entry.name: entry for entry in _envregistry.all_vars()}
        assert self.records, (
            "the central env-var registry is empty -- the nine owning-module side-effect imports did not run"
        )
        self.readme_section = _extract_markdown_section(
            README_MD.read_text(encoding="utf-8"), README_ENV_SECTION_HEADING
        )

    def test_every_registered_var_is_named_in_the_section(self) -> None:
        missing: list[str] = []
        for name in sorted(self.records):
            if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", self.readme_section) is None:
                missing.append(name)
        self.assertEqual(
            [],
            missing,
            "registered environment variables missing from the README's 'Environment Variables' section "
            "(feat-208, REQ-004/ACC-004; the section runs from its own heading to the next heading of the "
            "same or higher level): " + ", ".join(missing),
        )


class TestServerJsonEnvironmentVariablesCoverage(unittest.TestCase):
    """REQ-004/ACC-004: every registered variable has a manifest entry with a faithful `default`/`choices`/`format`."""

    def setUp(self) -> None:
        self.records: dict[str, _envregistry.EnvVar] = {entry.name: entry for entry in _envregistry.all_vars()}
        assert self.records, (
            "the central env-var registry is empty -- the nine owning-module side-effect imports did not run"
        )
        self.manifest_entries = _manifest_env_vars()

    def test_every_registered_var_has_a_manifest_entry(self) -> None:
        missing = [name for name in sorted(self.records) if name not in self.manifest_entries]
        self.assertEqual(
            [],
            missing,
            "registered environment variables missing from server.json's environmentVariables "
            "(feat-208, REQ-004/ACC-004): " + ", ".join(missing),
        )

    def test_manifest_default_field_is_faithful(self) -> None:
        drift: list[str] = []
        tempdir = tempfile.gettempdir()
        for name in sorted(self.records):
            entry = self.manifest_entries.get(name)
            if entry is None:
                continue  # named by test_every_registered_var_has_a_manifest_entry
            record = self.records[name]
            record_has_default = record.default is not None
            manifest_has_default = "default" in entry
            if record_has_default != manifest_has_default:
                drift.append(
                    f"{name}.default (registry: {'present' if record_has_default else 'absent'}, "
                    f"manifest: {'present' if manifest_has_default else 'absent'})"
                )
                continue
            if record.default is None:
                continue  # both sides absent: nothing to compare
            default = record.default
            normalized = default
            placeholder_changed = False
            if normalized.startswith(tempdir + os.sep):
                normalized = _TEMPDIR_PLACEHOLDER + normalized[len(tempdir) :]
                placeholder_changed = True
            if placeholder_changed and name not in _TEMPDIR_PLACEHOLDER_VARS:
                drift.append(
                    f"{name}.default (the <tempdir> placeholder normalization changed the registry default "
                    f"{default!r}, but {name} is not one of the placeholder-documented variables "
                    f"{sorted(_TEMPDIR_PLACEHOLDER_VARS)} -- the placeholder convention must not leak in silently)"
                )
                continue
            if entry["default"] != normalized:
                drift.append(f"{name}.default (manifest: {entry['default']!r}, registry: {default!r})")
        self.assertEqual(
            [],
            drift,
            "server.json's environmentVariables drifted from the registry defaults (feat-208, REQ-004/ACC-004): "
            + "; ".join(drift),
        )

    def test_manifest_choices_field_is_faithful(self) -> None:
        drift: list[str] = []
        for name in sorted(self.records):
            entry = self.manifest_entries.get(name)
            if entry is None:
                continue  # named by test_every_registered_var_has_a_manifest_entry
            record = self.records[name]
            manifest_choices = entry.get("choices")
            if manifest_choices is None:
                manifest_value: list[object] = []
            elif not isinstance(manifest_choices, list):
                drift.append(f"{name}.choices (manifest value {manifest_choices!r} is not a list)")
                continue
            else:
                manifest_value = manifest_choices
            if manifest_value != list(record.choices):
                drift.append(f"{name}.choices (manifest: {manifest_value!r}, registry: {list(record.choices)!r})")
        self.assertEqual(
            [],
            drift,
            "server.json's environmentVariables drifted from the registry choices (feat-208, REQ-004/ACC-004): "
            + "; ".join(drift),
        )

    def test_manifest_format_field_is_faithful(self) -> None:
        drift: list[str] = []
        for name in sorted(self.records):
            entry = self.manifest_entries.get(name)
            if entry is None:
                continue  # named by test_every_registered_var_has_a_manifest_entry
            record = self.records[name]
            manifest_format = entry.get("format")
            if manifest_format is not None and not isinstance(manifest_format, str):
                drift.append(f"{name}.format (manifest value {manifest_format!r} is not a string)")
                continue
            if manifest_format != record.format:
                drift.append(f"{name}.format (manifest: {manifest_format!r}, registry: {record.format!r})")
        self.assertEqual(
            [],
            drift,
            "server.json's environmentVariables drifted from the registry format (feat-208, REQ-004/ACC-004): "
            + "; ".join(drift),
        )


class TestTyperMcpOptionDefaults(unittest.TestCase):
    """ACC-002: the three `specmgr mcp` Typer options source their defaults from the registry records."""

    def setUp(self) -> None:
        self.records: dict[str, _envregistry.EnvVar] = {entry.name: entry for entry in _envregistry.all_vars()}
        assert self.records, (
            "the central env-var registry is empty -- the nine owning-module side-effect imports did not run"
        )
        self.mcp_source = MCP_COMMAND_PATH.read_text(encoding="utf-8")
        self.mcp_globals: dict[str, object] = dict(vars(sys.modules["biz.dfch.specmgr.commands.mcp"]))
        sites = scan_env_var_read_sites()
        self.option_sites: dict[str, list] = {var: [] for var in _MCP_OPTION_VARS}
        for var, var_sites in sites.items():
            if var in self.option_sites:
                self.option_sites[var] = [
                    site for site in var_sites if site.file == MCP_COMMAND_PATH and site.shape == SHAPE_TYPER_ENVVAR
                ]

    def test_each_option_default_is_a_registry_record_reference(self) -> None:
        problems: list[str] = []
        tree = ast.parse(self.mcp_source)
        for var in _MCP_OPTION_VARS:
            record = self.records.get(var)
            if record is None:
                problems.append(f"{var} is not registered in the central env-var registry")
                continue
            sites = self.option_sites.get(var, [])
            if len(sites) != 1:
                problems.append(f"{var} has {len(sites)} Typer envvar option site(s) in commands/mcp.py (expected 1)")
                continue
            expression = typer_option_default_expression(self.mcp_source, sites[0].line)
            if expression is None or expression == "":
                problems.append(f"{var}'s Typer option in commands/mcp.py carries no extractable `default=` expression")
                continue
            match = _REGISTRY_REF_RE.fullmatch(expression)
            if match is None:
                problems.append(
                    f"{var}'s Typer option default is the raw expression {expression!r}, not a reference to the "
                    "registry record's default (expected `<identifier>.default` or `int(<identifier>.default)`) "
                    f"-- the registry is the authority for the default, not a duplicated literal"
                )
                continue
            binding = _registered_record_binding(tree, var)
            if binding is None:
                problems.append(
                    f'{var} has no module-level `_envregistry.register("{var}", ...)` binding in commands/mcp.py'
                )
                continue
            if binding != match.group(1):
                problems.append(
                    f"{var}'s Typer option default references {match.group(1)!r}, but commands/mcp.py registers "
                    f"{var} as {binding!r}"
                )
        self.assertEqual(
            [],
            problems,
            "the specmgr mcp Typer options' defaults drifted from the registry (feat-208, ACC-002): "
            + "; ".join(problems),
        )

    def test_each_option_default_evaluates_to_the_registry_default(self) -> None:
        problems: list[str] = []
        for var in _MCP_OPTION_VARS:
            record = self.records.get(var)
            if record is None or record.default is None:
                continue  # named by the other tests
            sites = self.option_sites.get(var, [])
            if len(sites) != 1:
                continue  # named by the other tests
            expression = typer_option_default_expression(self.mcp_source, sites[0].line)
            if expression is None or expression == "":
                continue  # named by the other tests
            expected = int(record.default) if expression.startswith("int(") else record.default
            value = eval(expression, self.mcp_globals)  # the expression is regex-validated as a record reference
            if value != expected:
                problems.append(
                    f"{var}'s Typer option default {expression!r} evaluates to {value!r}, but the registry "
                    f"default is {record.default!r}"
                )
        self.assertEqual(
            [],
            problems,
            "the specmgr mcp Typer options' evaluated defaults drifted from the registry (feat-208, ACC-002): "
            + "; ".join(problems),
        )


if __name__ == "__main__":
    unittest.main()
