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
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

#: The repository root (this test lives in `tests/`, one level below it).
REPO_ROOT = Path(__file__).resolve().parents[1]

#: The hand-maintained manifest this test guards.
SERVER_JSON = REPO_ROOT / "server.json"

#: The prefix every manifest-relevant environment variable name carries.
_ENV_NAME_PATTERN = r"SPECMGR_[A-Z0-9_]+"

#: A quoted environment-variable name; the backreference keeps the quotes matched.
_QUOTED_NAME_PATTERN = rf'(?P<quote>["\'])(?P<name>{_ENV_NAME_PATTERN})(?P=quote)'

#: Shape (1): a string-literal assignment -- `CONST = "SPECMGR_..."` (the `_*_ENV_VAR`
#: constants). The lvalue is required to be an UPPER_CASE identifier: it is the constant
#: the name is read through, and a lower/lower-mixed lvalue (e.g. Typer's own `envvar=`
#: keyword) is not a constant declaration.
SHAPE_ASSIGNMENT = "string-literal-assignment"
#: Shape (2): a `getenv("SPECMGR_...")` call site.
SHAPE_GETENV = "getenv-call"
#: Shape (3): an `environ["SPECMGR_..."]` / `environ.get("SPECMGR_...")` access.
SHAPE_ENVIRON = "environ-access"
#: Shape (4): a Typer `envvar="SPECMGR_..."` option.
SHAPE_TYPER_ENVVAR = "typer-envvar-option"

#: Shape (1): UPPER_CASE constant `=` quoted name (see the `SHAPE_ASSIGNMENT` note).
_SHAPE_ASSIGNMENT_RE = re.compile(rf"(?<![\w.])(?P<const>[A-Z_][A-Z0-9_]*)\s*=\s*{_QUOTED_NAME_PATTERN}")
#: Shape (2): `getenv(` quoted name; the `\s*` also bridges multi-line call formatting.
_SHAPE_GETENV_RE = re.compile(rf"(?<!\w)getenv\(\s*{_QUOTED_NAME_PATTERN}")
#: Shape (3): `environ[` quoted name (subscript access).
_SHAPE_ENVIRON_SUBSCRIPT_RE = re.compile(rf"(?<!\w)environ\[\s*{_QUOTED_NAME_PATTERN}")
#: Shape (3): `environ.get(` quoted name (get access).
_SHAPE_ENVIRON_GET_RE = re.compile(rf"(?<!\w)environ\.get\(\s*{_QUOTED_NAME_PATTERN}")
#: Shape (4): `envvar =` quoted name (Typer option, spacing around the `=` optional).
_SHAPE_TYPER_ENVVAR_RE = re.compile(rf"(?<!\w)envvar\s*=\s*{_QUOTED_NAME_PATTERN}")

#: The (shape label, pattern) pairs, in the plan's shape-numbering order.
_SHAPE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (SHAPE_ASSIGNMENT, _SHAPE_ASSIGNMENT_RE),
    (SHAPE_GETENV, _SHAPE_GETENV_RE),
    (SHAPE_ENVIRON, _SHAPE_ENVIRON_SUBSCRIPT_RE),
    (SHAPE_ENVIRON, _SHAPE_ENVIRON_GET_RE),
    (SHAPE_TYPER_ENVVAR, _SHAPE_TYPER_ENVVAR_RE),
)

#: How far forward (in lines) the Annotated-option default scan may look past the
#: `envvar=` line before giving up (no default).
_TYPER_DEFAULT_SCAN_LIMIT = 40

#: An Annotated close carrying the parameter default: `] = <value>` (the modern Typer
#: style sits the default on the line closing the Annotated wrapper, below `envvar=`).
_ANNOTATED_DEFAULT_RE = re.compile(r"^\s*\]\s*=")
#: An Annotated close without a default: `]` followed directly by a separator.
_ANNOTATED_NO_DEFAULT_RE = re.compile(r"^\s*\]\s*[),\]]")
#: A function-signature close (the option's Annotated never closed with a default).
_SIGNATURE_END_RE = re.compile(r"^\s*\)\s*(?::|->|$)")
#: A new parameter starting (a defensive scan bound).
_NEW_PARAMETER_RE = re.compile(r"^\s*[A-Za-z_]\w*\s*:\s*Annotated\s*\[")


@dataclass(frozen=True)
class EnvVarReadSite:
    """One environment-variable read site found by the source scan.

    Attributes:
        file: The source file the site was found in (absolute path).
        line: The 1-based line number the quoted name sits on.
        shape: Which syntactic shape matched (one of the `SHAPE_*` constants).
        name: The environment-variable name the site reads.
        constant: For a shape-(1) site, the UPPER_CASE identifier the name is assigned
            to (the constant the name's read sites are followed through); `None` for
            the other shapes (the name sits in a quoted literal at the site itself).
    """

    file: Path
    line: int
    shape: str
    name: str
    constant: str | None


def _find_triple_close(line: str, quote: str, start: int) -> int:
    """The index of the first unescaped triple-quote occurrence at/after `start`, or -1.

    Args:
        line: The source line to search.
        quote: The quote character whose triple form delimits the string (`"` or `'`).
        start: The index to start searching from (past the opening delimiter).

    Returns:
        The index of the closing delimiter, or -1 when the line does not close the string.
    """
    triple = quote * 3
    index = start
    while True:
        found = line.find(triple, index)
        if found == -1:
            return -1
        backslashes = 0
        position = found - 1
        while position >= 0 and line[position] == "\\":
            backslashes += 1
            position -= 1
        if backslashes % 2 == 0:
            return found
        index = found + 1


def _code_lines(text: str) -> list[str]:
    """Reduce raw source text to per-line code text for the shape scan.

    Triple-quoted (docstring) regions are blanked line by line, and `#` comments
    outside string literals are stripped, so the shape patterns only ever see code:
    docstring prose or a comment that merely mentions a `SPECMGR_*` name -- or even
    quotes one of the read-site shapes verbatim -- must not be reported (ACC-004).
    The line count is preserved, so output entry `i` is input line `i + 1`.

    Args:
        text: The raw source text of one `.py` file.

    Returns:
        One code-text string per input line (same count, same order).
    """
    result: list[str] = []
    docstring_quote: str | None = None
    for line in text.split("\n"):
        if docstring_quote is not None:
            close_index = _find_triple_close(line, docstring_quote, 0)
            if close_index == -1:
                result.append("")
                continue
            line = line[close_index + 3 :]
            docstring_quote = None
        chars: list[str] = []
        in_string: str | None = None
        index = 0
        length = len(line)
        while index < length:
            char = line[index]
            if in_string is not None:
                chars.append(char)
                if char == "\\" and index + 1 < length:
                    chars.append(line[index + 1])
                    index += 2
                    continue
                if char == in_string:
                    in_string = None
                index += 1
                continue
            if char == "#":
                break
            if char in ("'", '"') and line.startswith(char * 3, index):
                close_index = _find_triple_close(line, char, index + 3)
                if close_index == -1:
                    docstring_quote = char
                    break
                index = close_index + 3
                continue
            if char in ("'", '"'):
                in_string = char
            chars.append(char)
            index += 1
        result.append("".join(chars))
    return result


def _iter_source_files(root: Path) -> list[Path]:
    """Every `.py` file under `root/src`, in sorted (deterministic) order.

    Args:
        root: The repository root to scan.

    Returns:
        The sorted list of source file paths.

    Raises:
        AssertionError: When `root/src` is not a directory (a fixture tree must mirror
            the repo's own layout).
    """
    assert (root / "src").is_dir(), f"no src/ directory under {root}"
    result = sorted((root / "src").glob("**/*.py"))
    return result


def _scan_tree(root: Path) -> tuple[dict[str, list[EnvVarReadSite]], dict[Path, str]]:
    """One pass over `root/src/**/*.py`: the shape read sites, plus each file's code text.

    Args:
        root: The repository root to scan.

    Returns:
        The read sites keyed by environment-variable name (insertion order: first
        file/line found), and the per-file code text (docstring regions and comments
        blanked) that the default-presence classification runs over.
    """
    sites: dict[str, list[EnvVarReadSite]] = {}
    code_texts: dict[Path, str] = {}
    for path in _iter_source_files(root):
        code_text = "\n".join(_code_lines(path.read_text(encoding="utf-8")))
        code_texts[path] = code_text
        for shape, pattern in _SHAPE_PATTERNS:
            for match in pattern.finditer(code_text):
                name = match.group("name")
                site_line = code_text.count("\n", 0, match.start("name")) + 1
                constant = match.group("const") if "const" in match.groupdict() else None
                sites.setdefault(name, []).append(
                    EnvVarReadSite(file=path, line=site_line, shape=shape, name=name, constant=constant)
                )
    return sites, code_texts


def scan_env_var_read_sites(root: Path = REPO_ROOT) -> dict[str, list[EnvVarReadSite]]:
    """Scan `root/src/**/*.py` for `SPECMGR_*` environment-variable read sites.

    Args:
        root: The repository root (default: this checkout's own root, so fixture tests
            can point the scan at a synthetic tree instead).

    Returns:
        The read sites keyed by environment-variable name; a name is reported iff at
        least one of the four shapes finds it. Docstring prose, comments, and
        identifiers that merely contain the prefix (e.g. `_SPECMGR_ROOT`) never match.
    """
    assert isinstance(root, Path), type(root)
    result, _code_texts = _scan_tree(root)
    return result


def _compile_read_patterns(needle: str) -> tuple[re.Pattern[str], ...]:
    """The per-read-site classification patterns for one needle, in verdict order.

    Args:
        needle: The regex fragment identifying the read target -- the bare constant
            identifier (shape (1)) or the quote-agnostic quoted name (shapes (2)/(3)).

    Returns:
        Eight compiled patterns: an explicit second argument (default present), a
        membership test (no default), a subscript access (no default), an
        explicit-`None`-comparison presence check (no default), a line-anchored
        conditional presence read -- an `if [not] get(NEEDLE):` statement, a
        truthiness test (no default) --, a line-anchored plain-`get` read in an
        assignment context (default present -- the corpus's pre-migration genuine
        default shape: a statement line whose entire code is
        `<identifier> = get(NEEDLE)`, the line ending right after the call's closing
        paren, the caller applying the fallback, e.g. `Path(value) if value else
        DEFAULT_X`), the central env-var registry's `get_with_default(NEEDLE)`
        accessor call (default present -- the post-migration corpus read shape,
        feat-208 Phase 120: the accessor itself inserts the registered default, so
        the call's context carries no further classification), and the registry's
        raw `get(NEEDLE)` accessor call (no default -- the presence-based read,
        whose whole point is the `None`-vs-set distinction). The conditional and
        assignment-context patterns are compiled with `re.MULTILINE`; the
        assignment-context pattern replaces the former substring plain-`get`
        pattern, whose negative lookahead could not exclude a conditional
        truthiness read (`if os.environ.get(NEEDLE):`) that is a presence check,
        now carried by its own line-anchored pattern.
    """
    result = (
        re.compile(rf"(?<!\w)(?:environ\.get|getenv)\(\s*{needle}\s*,"),
        re.compile(rf"{needle}\s+in\s+os\.environ"),
        re.compile(rf"(?<!\w)environ\[\s*{needle}\s*\]"),
        re.compile(rf"(?<!\w)(?:environ\.get|getenv)\(\s*{needle}\s*\)\s*is\s+(?:not\s+)?None"),
        re.compile(rf"(?m)^\s*if\s+(?:not\s+)?(?:os\.)?(?:environ\.get|getenv)\(\s*{needle}\s*\)\s*:"),
        re.compile(rf"(?m)^\s*[A-Za-z_]\w*\s*=\s*(?:os\.)?(?:environ\.get|getenv)\(\s*{needle}\s*\)\s*$"),
        re.compile(rf"(?<!\w)_envregistry\.get_with_default\(\s*{needle}\s*\)"),
        re.compile(rf"(?<!\w)_envregistry\.get\(\s*{needle}\s*\)"),
    )
    return result


def _read_verdict(code_text: str, patterns: tuple[re.Pattern[str], ...]) -> bool | None:
    """Classify one file's reads of a needle.

    Args:
        code_text: One whole file's code text (docstring regions and comments blanked).
        patterns: The needle's compiled read patterns, in verdict order (see
            `_compile_read_patterns`).

    Returns:
        True when at least one read carries a code-side default (an explicit second
        argument, a line-anchored plain-`get` read in an assignment context, or the
        registry's `get_with_default` accessor call), False when the file reads the
        needle only through the no-default shapes (a membership test, a subscript
        access, an explicit-`None`-comparison presence check, a line-anchored
        conditional presence read, or the registry's raw `get` accessor call), and
        None when the file does not read the needle at all.
    """
    has_default = (
        patterns[0].search(code_text) is not None
        or patterns[5].search(code_text) is not None
        or patterns[6].search(code_text) is not None
    )
    if has_default:
        return True
    reads_without_default = (
        patterns[1].search(code_text) is not None
        or patterns[2].search(code_text) is not None
        or patterns[3].search(code_text) is not None
        or patterns[4].search(code_text) is not None
        or patterns[7].search(code_text) is not None
    )
    if reads_without_default:
        return False
    return None


def _needle_for_site(site: EnvVarReadSite) -> tuple[str, str]:
    """The (regex needle, plain prefilter substring) for a shape-(1)/(2)/(3) site.

    A shape-(1) site tracks the name through its assigned constant (the bare
    identifier); a shape-(2)/(3) site reads the name as a quoted literal, so its
    needle is quote-agnostic (single- or double-quoted) and its prefilter is the bare
    name.

    Args:
        site: The read site whose needle to derive.

    Returns:
        The needle pattern fragment and the cheap substring used to skip files that
        cannot possibly read it.
    """
    if site.shape == SHAPE_ASSIGNMENT:
        assert site.constant, site
        result: tuple[str, str] = (re.escape(site.constant), site.constant)
        return result
    result = (rf'["\']{re.escape(site.name)}["\']', site.name)
    return result


def _typer_option_has_default(code_text: str, envvar_line: int) -> bool:
    """Whether the Annotated parameter carrying the `envvar=` option on `envvar_line` closes with a default.

    The modern Typer style (`Annotated[str, typer.Option(...)] = <default>`) sits the
    parameter default on the line closing the Annotated wrapper (`] = <value>`), a few
    lines below the `envvar=` line. An `]` without an assignment, a signature close, or
    a new `Annotated[` parameter before any close means the option carries no default.

    Args:
        code_text: The option's own file's code text.
        envvar_line: The 1-based line number the `envvar=` match sat on.

    Returns:
        True iff the forward scan finds the Annotated close + assignment shape.
    """
    result: bool = False
    for line_no, line_text in enumerate(code_text.split("\n"), start=1):
        if line_no <= envvar_line:
            continue
        if line_no > envvar_line + _TYPER_DEFAULT_SCAN_LIMIT:
            break
        if _ANNOTATED_DEFAULT_RE.match(line_text):
            result = True
            break
        if _ANNOTATED_NO_DEFAULT_RE.match(line_text) or _SIGNATURE_END_RE.match(line_text):
            result = False
            break
        if _NEW_PARAMETER_RE.match(line_text):
            result = False
            break
    return result


def _name_has_code_default(name_sites: list[EnvVarReadSite], code_texts: dict[Path, str]) -> bool:
    """Whether at least one of a name's read sites carries a code-side default.

    A name's sites are OR'ed: a single default-carrying read (an explicit second
    argument, the corpus's assignment-context plain-`get` + caller-applied-fallback
    pattern, the registry's `get_with_default` accessor call, or an Annotated option
    default) suffices. The presence-based feature gates, the PlantUML source
    selectors, and the test/CI dotenv sentinel have no such site (only
    presence-check reads), which is exactly why their manifest entries carry no
    `default`.

    Args:
        name_sites: Every read site of one name, in file/line order.
        code_texts: The scanned files' code text, keyed by file (the default
            classification runs over the whole tree, since a shape-(1) constant is
            read at use sites that sit in other modules).

    Returns:
        True iff any site classifies as a default-carrying read.
    """
    for site in name_sites:
        if site.shape == SHAPE_TYPER_ENVVAR:
            if _typer_option_has_default(code_texts[site.file], site.line):
                return True
            continue
        needle, prefilter = _needle_for_site(site)
        patterns = _compile_read_patterns(needle)
        for _path, code_text in code_texts.items():
            if prefilter not in code_text:
                continue
            if _read_verdict(code_text, patterns) is True:
                return True
    return False


def env_var_code_defaults(root: Path = REPO_ROOT) -> dict[str, bool]:
    """Classify, for every name read in `root/src`, whether the code carries a default.

    Args:
        root: The repository root (default: this checkout's own root, so fixture tests
            can point the classification at a synthetic tree instead).

    Returns:
        `name -> True` iff at least one of the name's read sites is a read with a
        code-side default, `False` otherwise (presence-only reads -- explicit
        `None`-comparison or conditional, subscript reads, or an undetermined read).
    """
    assert isinstance(root, Path), type(root)
    sites, code_texts = _scan_tree(root)
    result: dict[str, bool] = {}
    for name, name_sites in sites.items():
        result[name] = _name_has_code_default(name_sites, code_texts)
    return result


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
