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

"""``plantuml-check`` -- validate any ``.puml`` file(s) through the strict chain (feat-185-uc-diagrams, Phase 130).

The CLI half of the chain's distinct value: it validates **any committed
``.puml`` file** — including the agent-owned ``<id>.sequence.puml`` files
that ``diagram uc`` never touches — without a specmgr document and without
an MCP client (plan Overview layer 3 — thin, no new logic). It reads each
file and passes the text to ``plantuml.chain.validate_plantuml`` (rulebook
§3: the structure pre-flight always, then the single first-set-wins source;
the §3.6 result is non-raising).

Per file, the console shows the verdict (``checked_by``, ``valid``,
``rendered``, ``source_state`` — ``None`` prints as ``not-run``, rulebook
§3.6) plus every error/warning finding as
``{path}:{line}: {message} (fix: {fix_hint})`` (actionable, the feat-27
convention; warnings carry a ``warning:`` tag, and line 0 — the URL
backend's parser-level findings — prints without a line number). For a
set-but-unavailable source or a persistent inconclusive verdict, the
chain's own ``reason``/``fix_hint`` are printed as well.

Exit codes (pinned, REQ-009), across the whole invocation — with multiple
files and mixed verdicts, the **worst applicable code wins, by severity
``2 > 3 > 1 > 0``** (rationale: a misconfigured/unavailable source (2) or an
inconclusive verdict (3) means the content verdicts are not trustworthy and
outrank a plain content verdict; 2 and 3 cannot co-occur within one
invocation — one source per invocation — but the total order is pinned):

* ``0`` — every file is valid at the highest available layer (structure
  green + source green where a source ran — including the all-unset
  structure-only floor: structure green ⇒ 0)
* ``1`` — any file is structure-red (the §3.7 short-circuit) or
  source-invalid
* ``2`` — the selected source is set but misconfigured/unavailable (the
  chain's hard failure — ``reason``/``fix_hint`` reported), or a usage
  error: a non-``.puml`` path or a missing/unreadable file (all usage
  problems of the invocation are reported before any chain run)
* ``3`` — the source's verdict is inconclusive (persistent after the
  chain's one retry) — including the URL matrix's undetermined
  request-error/encode-error rows (``valid=None`` at a source that ran),
  which are never INVALID (rulebook §5.2)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ..plantuml import chain
from ..plantuml.chain import PlantumlValidationResult
from ..plantuml.structure import Finding

__all__ = [
    "EXIT_INCONCLUSIVE",
    "EXIT_INVALID",
    "EXIT_SOURCE_FAILURE",
    "EXIT_VALID",
    "plantuml_check",
]

#: The pinned exit codes (see the module docstring for the full table).
EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_SOURCE_FAILURE = 2
EXIT_INCONCLUSIVE = 3

#: The worst-code-wins severity per exit code (the plan's ``2 > 3 > 1 > 0``
#: order — a broken source or an inconclusive verdict outranks a plain
#: content verdict because it makes the content verdicts untrustworthy).
_SEVERITY_BY_CODE = {EXIT_VALID: 0, EXIT_INVALID: 1, EXIT_INCONCLUSIVE: 2, EXIT_SOURCE_FAILURE: 3}
_CODE_BY_SEVERITY = {severity: code for code, severity in _SEVERITY_BY_CODE.items()}

#: The ``source_state`` values for which the chain's own ``reason``/``fix_hint`` are printed.
_SOURCE_FAILURE_STATES = (chain.STATE_MISCONFIGURED, chain.STATE_UNAVAILABLE, chain.STATE_INCONCLUSIVE)


def _bool_word(value: bool | None) -> str:
    """The verdict word for one ``valid``/``rendered`` field (``None`` = not run, rulebook §3.6)."""
    assert isinstance(value, bool) or value is None, value
    if value is True:
        result = "true"
    elif value is False:
        result = "false"
    else:
        result = "not-run"
    return result


def _file_exit_code(result: PlantumlValidationResult) -> int:
    """Map one file's §3.6 result to this command's pinned exit code (the module docstring's table)."""
    if not result.structure_ok:
        return EXIT_INVALID  # structure red: the §3.7 short-circuit (the parser was never called)
    if result.valid is False:
        return EXIT_INVALID  # the authoritative source said invalid
    if result.valid is True:
        return EXIT_VALID
    # ``valid is None`` — a source-level state, never a content verdict:
    if result.source_state in (chain.STATE_MISCONFIGURED, chain.STATE_UNAVAILABLE):
        return EXIT_SOURCE_FAILURE  # the chain's hard failure (no source ran)
    if result.source_state == chain.STATE_INCONCLUSIVE:
        return EXIT_INCONCLUSIVE  # persistent after the chain's one retry
    if result.available:
        return EXIT_INCONCLUSIVE  # the source ran but produced no verdict (the URL matrix's
        # request-error/encode-error rows — never INVALID, rulebook §5.2)
    return EXIT_VALID  # the all-unset structure-only floor: structure green ⇒ valid


def _print_finding(path_str: str, finding: Finding, *, warning: bool) -> None:
    """One finding line: ``{path}:{line}: {message} (fix: {fix_hint})`` (feat-27 convention)."""
    assert isinstance(finding, Finding), type(finding)
    prefix = f"{path_str}:{finding.line}" if finding.line >= 1 else path_str
    tag = "warning: " if warning else ""
    typer.echo(f"{prefix}: {tag}{finding.message} (fix: {finding.fix_hint})")


def _print_verdict(path_str: str, result: PlantumlValidationResult) -> None:
    """The per-file verdict block (the console contract in the module docstring)."""
    typer.echo(
        f"{path_str}: checked_by={result.checked_by} valid={_bool_word(result.valid)} "
        f"rendered={_bool_word(result.rendered)} source_state={result.source_state}"
    )
    for finding in result.errors:
        _print_finding(path_str, finding, warning=False)
    for finding in result.warnings:
        _print_finding(path_str, finding, warning=True)
    if result.source_state in _SOURCE_FAILURE_STATES and result.reason is not None:
        typer.echo(f"{path_str}: {result.reason}")
        if result.fix_hint is not None:
            typer.echo(f"{path_str}: fix: {result.fix_hint}")


def plantuml_check(
    paths: Annotated[
        list[str],
        typer.Argument(help="One or more .puml files to validate (agent-owned sequence files included)."),
    ],
) -> None:
    """Validate one or more ``.puml`` files through the strict chain (rulebook §3).

    Every path must be a readable ``.puml`` file (a non-``.puml`` or
    missing/unreadable path is a usage error — exit 2, all problems of the
    invocation reported before any chain run). Each file's text goes through
    ``plantuml.chain.validate_plantuml``; the per-file verdict and findings
    are printed (see the module docstring), and the invocation exits with
    the worst applicable code by the pinned severity order
    ``2 > 3 > 1 > 0``.
    """
    usage_errors: list[str] = []
    texts: list[tuple[str, str]] = []
    for path_str in paths:
        path = Path(path_str)
        if path.suffix != ".puml":
            usage_errors.append(f"{path_str}: not a .puml file (usage error)")
            continue
        try:
            texts.append((path_str, path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError) as ex:
            usage_errors.append(f"{path_str}: unreadable ({ex}) (usage error)")
    if usage_errors:
        for error in usage_errors:
            typer.echo(f"error: {error}", err=True)
        raise typer.Exit(EXIT_SOURCE_FAILURE)

    worst_severity = 0
    for path_str, text in texts:
        result = chain.validate_plantuml(text)
        _print_verdict(path_str, result)
        worst_severity = max(worst_severity, _SEVERITY_BY_CODE[_file_exit_code(result)])
    raise typer.Exit(_CODE_BY_SEVERITY[worst_severity])
