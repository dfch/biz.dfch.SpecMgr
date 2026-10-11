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

"""Shared environment-variable read-site scanner over `src/**/*.py` (feat-208, Task 150.100).

Extracted, behaviour-preserving, from feat-126-server-json-env-drift's drift
test (`tests/test_server_json.py`, which still pins the manifest side and the
scan's negative fixtures): the four syntactic read-site shapes (string-literal
assignment, `getenv` call, `environ` access, Typer `envvar=` option), the
docstring/comment blanking, the eight-pattern default-presence classifier, and
the Typer `Annotated` option-default scan. The consumers are:

* `tests/test_server_json.py` -- feat-126's bidirectional `server.json` drift
  guard (since feat-208 Phase 160 its `setUp` runs on the registry-aware
  `discovery_name_pattern` -- the `SPECMGR_` prefix net union the quoted form
  of every registered name -- so the manifest's third-party
  `FASTEMBED_CACHE_PATH` entry is visible to the scan; the assertions are
  unchanged), and
* `tests/test_envregistry_completeness.py` -- feat-208's registry-to-source
  completeness test (REQ-003), which passes the same broadened name pattern
  (the helper's own `discovery_name_pattern`).

The scan is a regex over source text with `#` comments and triple-quoted
(docstring) regions blanked -- not a full parser (the plan pins the line-regex
design, with tightening as the sanctioned remedy for false positives; this
blanking is that tightening, pinned by feat-126's negative fixtures). A
single-line string whose content quotes one of the shapes verbatim is a known
accepted limitation (no such line exists in the corpus, and one would fail
visibly, naming the entry, if introduced). The default-presence classifier is
line-anchored where it needs line context, for the same reason.

The module is import-clean: it reads source text only, mutates nothing (in
particular the env-var registry), and registers no tests.

Name-pattern parameterization: every public scan entry point takes
`name_pattern` (default `DEFAULT_NAME_PATTERN`, feat-126's own `SPECMGR_`
prefix net -- the default keeps feat-126's behaviour byte-identical). The
pattern is inserted verbatim as the `(?P<name>...)` group of the quoted-name
pattern, so a caller-supplied alternation (e.g. `SPECMGR_[A-Z0-9_]+|
FASTEMBED_CACHE_PATH`) scopes itself inside that group and needs no extra
parenthesizing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "DEFAULT_NAME_PATTERN",
    "EnvVarReadSite",
    "REPO_ROOT",
    "SHAPE_ASSIGNMENT",
    "SHAPE_ENVIRON",
    "SHAPE_GETENV",
    "SHAPE_TYPER_ENVVAR",
    "discovery_name_pattern",
    "env_var_code_defaults",
    "scan_env_var_read_sites",
    "typer_option_default_expression",
]

#: The repository root (this module lives in `tests/`, one level below it).
REPO_ROOT = Path(__file__).resolve().parents[1]

#: The default environment-variable name pattern: the `SPECMGR_` prefix net
#: every manifest-relevant specmgr variable carries (feat-126's own pattern --
#: the default keeps a default-pattern call's scan behaviour byte-identical to
#: feat-126's pre-extraction test).
DEFAULT_NAME_PATTERN = r"SPECMGR_[A-Z0-9_]+"


def discovery_name_pattern(registered_names: set[str]) -> str:
    """The registry-aware discovery name pattern (feat-208, Phase 160).

    The `SPECMGR_` prefix net (the helper's own default,
    `DEFAULT_NAME_PATTERN`) stays in the pattern so an unregistered
    `SPECMGR_*` variable read in `src/` is still discovered and reported;
    every registered name the net does not already cover (the non-`SPECMGR_`
    names -- today the third-party `FASTEMBED_CACHE_PATH`) is added as its
    own `re.escape`d alternation, so those names become visible to the scan
    (the helper inserts the pattern verbatim as the quoted-name group, so the
    alternation scopes correctly). The pattern is built at test time from the
    registry's current name set (`_envregistry.all_vars()`); the callers are
    `tests/test_envregistry_completeness.py` (the registry-to-source
    completeness guard, feat-208 Phase 150) and `tests/test_server_json.py`
    (feat-126's manifest drift guard, whose `setUp` was wired onto this
    pattern in Phase 160 so the manifest can carry the third-party variable),
    both preceded by the nine owning-module side-effect imports that make the
    registry complete.

    Args:
        registered_names: The registry's current name set.

    Returns:
        The alternation pattern for `scan_env_var_read_sites`'s
        `name_pattern`.
    """
    alternatives: list[str] = [DEFAULT_NAME_PATTERN]
    alternatives.extend(re.escape(name) for name in sorted(registered_names) if not name.startswith("SPECMGR_"))
    result = "|".join(alternatives)
    return result


#: Shape (1): a string-literal assignment -- `CONST = "NAME"` (the `_*_ENV_VAR`
#: constants). The lvalue is required to be an UPPER_CASE identifier: it is the
#: constant the name is read through, and a lower/lower-mixed lvalue (e.g.
#: Typer's own `envvar=` keyword) is not a constant declaration.
SHAPE_ASSIGNMENT = "string-literal-assignment"
#: Shape (2): a `getenv("NAME")` call site.
SHAPE_GETENV = "getenv-call"
#: Shape (3): an `environ["NAME"]` / `environ.get("NAME")` access.
SHAPE_ENVIRON = "environ-access"
#: Shape (4): a Typer `envvar="NAME"` option.
SHAPE_TYPER_ENVVAR = "typer-envvar-option"


def _quoted_name_pattern(name_pattern: str) -> str:
    """The quoted-name pattern fragment for one name pattern.

    A quoted environment-variable name; the backreference keeps the quotes
    matched.

    Args:
        name_pattern: The regex fragment for the name itself (inserted verbatim
            as the `(?P<name>...)` group, so caller alternations scope
            correctly).

    Returns:
        The quoted-name pattern fragment.
    """
    result = rf'(?P<quote>["\'])(?P<name>{name_pattern})(?P=quote)'
    return result


def _shape_patterns(name_pattern: str) -> tuple[tuple[str, re.Pattern[str]], ...]:
    """The five (shape label, compiled pattern) pairs for one name pattern.

    The four syntactic shapes of the plan's Design Notes (shape (3) carries two
    access forms), in the plan's shape-numbering order.

    Args:
        name_pattern: The environment-variable name pattern (see
            `DEFAULT_NAME_PATTERN`).

    Returns:
        The compiled shape patterns.
    """
    quoted = _quoted_name_pattern(name_pattern)
    result: tuple[tuple[str, re.Pattern[str]], ...] = (
        # Shape (1): UPPER_CASE constant `=` quoted name (see the `SHAPE_ASSIGNMENT` note).
        (SHAPE_ASSIGNMENT, re.compile(rf"(?<![\w.])(?P<const>[A-Z_][A-Z0-9_]*)\s*=\s*{quoted}")),
        # Shape (2): `getenv(` quoted name; the `\s*` also bridges multi-line call formatting.
        (SHAPE_GETENV, re.compile(rf"(?<!\w)getenv\(\s*{quoted}")),
        # Shape (3): `environ[` quoted name (subscript access).
        (SHAPE_ENVIRON, re.compile(rf"(?<!\w)environ\[\s*{quoted}")),
        # Shape (3): `environ.get(` quoted name (get access).
        (SHAPE_ENVIRON, re.compile(rf"(?<!\w)environ\.get\(\s*{quoted}")),
        # Shape (4): `envvar =` quoted name (Typer option, spacing around the `=` optional).
        (SHAPE_TYPER_ENVVAR, re.compile(rf"(?<!\w)envvar\s*=\s*{quoted}")),
    )
    return result


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
    docstring prose or a comment that merely mentions an environment-variable name --
    or even quotes one of the read-site shapes verbatim -- must not be reported
    (ACC-004). The line count is preserved, so output entry `i` is input line
    `i + 1`.

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


def _scan_tree(
    root: Path, name_pattern: str = DEFAULT_NAME_PATTERN
) -> tuple[dict[str, list[EnvVarReadSite]], dict[Path, str]]:
    """One pass over `root/src/**/*.py`: the shape read sites, plus each file's code text.

    Args:
        root: The repository root to scan.
        name_pattern: The environment-variable name pattern (see
            `DEFAULT_NAME_PATTERN`).

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
        for shape, pattern in _shape_patterns(name_pattern):
            for match in pattern.finditer(code_text):
                name = match.group("name")
                site_line = code_text.count("\n", 0, match.start("name")) + 1
                constant = match.group("const") if "const" in match.groupdict() else None
                sites.setdefault(name, []).append(
                    EnvVarReadSite(file=path, line=site_line, shape=shape, name=name, constant=constant)
                )
    return sites, code_texts


def scan_env_var_read_sites(
    root: Path = REPO_ROOT, name_pattern: str = DEFAULT_NAME_PATTERN
) -> dict[str, list[EnvVarReadSite]]:
    """Scan `root/src/**/*.py` for environment-variable read sites.

    Args:
        root: The repository root (default: this checkout's own root, so fixture tests
            can point the scan at a synthetic tree instead).
        name_pattern: The environment-variable name pattern a quoted name must match
            (default: `DEFAULT_NAME_PATTERN`, the `SPECMGR_` prefix net -- pass a
            broadened alternation, e.g. the quoted form of every registered name, to
            make non-`SPECMGR_` variables visible to the scan; feat-208, REQ-003).

    Returns:
        The read sites keyed by environment-variable name; a name is reported iff at
        least one of the four shapes finds it. Docstring prose, comments, and
        identifiers that merely contain a matched name (e.g. `_SPECMGR_ROOT`) never
        match.
    """
    assert isinstance(root, Path), type(root)
    result, _code_texts = _scan_tree(root, name_pattern)
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


def typer_option_default_expression(code_text: str, envvar_line: int) -> str | None:
    """The default expression of the Annotated parameter carrying the `envvar=` option on `envvar_line`.

    The modern Typer style (`Annotated[str, typer.Option(...)] = <default>`) sits the
    parameter default on the line closing the Annotated wrapper (`] = <value>`), a few
    lines below the `envvar=` line. The forward scan (bounded by
    `_TYPER_DEFAULT_SCAN_LIMIT`) returns that expression's text verbatim: a quoted
    literal keeps its quotes (`"stdio"`), and a registry-sourced expression is
    returned exactly as written (`_mcp_transport_var.default`,
    `int(_mcp_port_var.default)` -- the post-Phase-140 corpus form, feat-208). The
    trailing parameter separator (`,`) is stripped. This is the extraction the
    feat-208 Phase 160 default-fidelity comparison consumes: it matches the returned
    text (evaluated or resolved) against the registry record's own default, so the
    expression text -- not a bool -- is the return shape.

    Args:
        code_text: The option's own file's code text.
        envvar_line: The 1-based line number the `envvar=` match sat on.

    Returns:
        The default expression text, `None` when the option carries no default (the
        scan hits an `]` without an assignment, a signature close, a new `Annotated[`
        parameter, or the scan limit first), or the empty string when the option
        closes with a bare `] =` and the expression continues on a following line (an
        option default is present -- the empty string is not `None` -- but no such
        line exists in the current corpus).
    """
    for line_no, line_text in enumerate(code_text.split("\n"), start=1):
        if line_no <= envvar_line:
            continue
        if line_no > envvar_line + _TYPER_DEFAULT_SCAN_LIMIT:
            return None
        match = _ANNOTATED_DEFAULT_RE.match(line_text)
        if match:
            expression = line_text[match.end() :].strip()
            if expression.endswith(","):
                expression = expression[:-1].rstrip()
            result: str | None = expression
            return result
        if _ANNOTATED_NO_DEFAULT_RE.match(line_text) or _SIGNATURE_END_RE.match(line_text):
            return None
        if _NEW_PARAMETER_RE.match(line_text):
            return None
    return None


def _typer_option_has_default(code_text: str, envvar_line: int) -> bool:
    """Whether the Annotated parameter carrying the `envvar=` option on `envvar_line` closes with a default.

    The bool-compatible surface of `typer_option_default_expression` for the
    default-presence classifier's own use.

    Args:
        code_text: The option's own file's code text.
        envvar_line: The 1-based line number the `envvar=` match sat on.

    Returns:
        True iff the forward scan finds the Annotated close + assignment shape.
    """
    result = typer_option_default_expression(code_text, envvar_line) is not None
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


def env_var_code_defaults(root: Path = REPO_ROOT, name_pattern: str = DEFAULT_NAME_PATTERN) -> dict[str, bool]:
    """Classify, for every name read in `root/src`, whether the code carries a default.

    Args:
        root: The repository root (default: this checkout's own root, so fixture tests
            can point the classification at a synthetic tree instead).
        name_pattern: The environment-variable name pattern a quoted name must match
            (default: `DEFAULT_NAME_PATTERN`; see `scan_env_var_read_sites`).

    Returns:
        `name -> True` iff at least one of the name's read sites is a read with a
        code-side default, `False` otherwise (presence-only reads -- explicit
        `None`-comparison or conditional, subscript reads, or an undetermined read).
    """
    assert isinstance(root, Path), type(root)
    sites, code_texts = _scan_tree(root, name_pattern)
    result: dict[str, bool] = {}
    for name, name_sites in sites.items():
        result[name] = _name_has_code_default(name_sites, code_texts)
    return result
