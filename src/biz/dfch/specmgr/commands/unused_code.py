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

"""``unused-code`` -- report unreferenced Python symbols, or (with ``--test``) test-only ones.

Thin, friendlier wrapper around ``vulture`` with two modes:

* **Default** -- scans ``--src`` (plus ``--whitelist``, if it exists) and reports every
  unreferenced symbol vulture finds, exactly like the enforced pre-commit hook/CI step
  (``uv run --frozen vulture src/ whitelist.py --min-confidence 60``), just without having to
  remember that invocation.
* **``--test``/``-t``** -- reports symbols vulture only considers "used" because the test suite
  references them, never production code itself. Vulture treats any reference to a name across
  every path it scans as "used", regardless of whether that reference lives in production code
  or in the test suite; this mode exploits that by scanning twice and diffing the two finding
  sets:

  1. Scan ``--src`` alone -- anything reported is either genuinely unreferenced, or only ever
     called from ``--tests``.
  2. Scan ``--src`` together with ``--tests`` -- names exercised exclusively by tests now count
     as "used" and drop out of the findings.

  Names present in (1) but not (2) are referenced exclusively from test code, never from
  production code itself -- a lead worth a manual look, since it may indicate an orphaned public
  surface, or may simply be a Pydantic field/public API that is legitimately exercised only from
  tests so far. This is a name-based heuristic, the same as vulture itself: matching is by
  symbol name, not by definition site, so a hit still needs a manual ``grep`` to confirm which
  definition it actually refers to before concluding anything should change.

See the "Detect unreferenced code with vulture" ADR for the full rationale and ``whitelist.py``
for the enforced-in-CI counterpart of the default mode.

Requires the ``test`` extra (``pip install biz-dfch-specmgr[test]``), since ``vulture`` is only
declared as a dependency there.
"""

from pathlib import Path
from typing import Annotated

import typer

# __file__ = src/biz/dfch/specmgr/commands/unused_code.py
_SRC_ROOT = Path(__file__).resolve().parent.parent  # src/biz/dfch/specmgr
_REPO_ROOT = _SRC_ROOT.parent.parent.parent.parent  # repo root
_DEFAULT_SRC_DIR = _REPO_ROOT / "src"
_DEFAULT_TESTS_DIR = _REPO_ROOT / "tests"
_DEFAULT_WHITELIST = _REPO_ROOT / "whitelist.py"
_DEFAULT_MIN_CONFIDENCE = 60


def _scan(vulture_cls: type, paths: list[Path], min_confidence: int) -> list:
    """Scan `paths` together with a fresh `Vulture` instance, returning the reported `Item`s.

    Args:
        vulture_cls: The `vulture.Vulture` class, injected so the optional `vulture` import
            only has to be attempted once, by the caller.
        paths: Directories/files scanned together in a single pass -- a reference to a name in
            any one path counts as "used" for a definition in another.
        min_confidence: Vulture confidence threshold (0-100); lower reports more findings, with
            more noise.

    Returns:
        The `vulture.core.Item` objects vulture reports, in vulture's own order.
    """
    assert paths, "paths must not be empty"
    assert 0 <= min_confidence <= 100, min_confidence

    vulture = vulture_cls()
    vulture.scavenge([str(path) for path in paths])
    result = vulture.get_unused_code(min_confidence=min_confidence)
    return result


def _unused_names(vulture_cls: type, paths: list[Path], min_confidence: int) -> set[str]:
    """Return just the reported symbol names from `_scan()`.

    Deliberately just names, not full `Item` objects -- vulture itself matches by name, not by
    definition site, so a name can be reported once even if several unrelated definitions share
    it. Used by `--test` mode, which relies on exactly that name-based comparison.
    """
    return {item.name for item in _scan(vulture_cls, paths, min_confidence)}


def _report_unused_code(vulture_cls: type, src: Path, whitelist: Path, min_confidence: int) -> bool:
    """Print every unreferenced symbol vulture finds in `src` (plus `whitelist`, if present).

    Returns:
        True if any findings were reported, False on a clean scan.
    """
    paths = [src, whitelist] if whitelist.exists() else [src]
    items = _scan(vulture_cls, paths, min_confidence)

    if not items:
        typer.echo(f"No unused code found in {src}.")
        return False

    for item in items:
        typer.echo(item.get_report())
    return True


def _report_test_only_usage(vulture_cls: type, src: Path, tests: Path, min_confidence: int) -> bool:
    """Print symbol names referenced only from `tests`, never from `src` itself.

    Returns:
        True if any findings were reported, False if none were found.
    """
    src_only = _unused_names(vulture_cls, [src], min_confidence)
    src_and_tests = _unused_names(vulture_cls, [src, tests], min_confidence)
    test_only = sorted(src_only - src_and_tests)

    if not test_only:
        typer.echo(f"No symbols in {src} are referenced exclusively from {tests}.")
        return False

    typer.echo(f"{len(test_only)} symbol name(s) referenced only from {tests}, never from {src} itself:")
    for name in test_only:
        typer.echo(f"  - {name}")
    typer.echo("")
    typer.echo(
        "Name-based signal only, not per-definition -- confirm each hit with a manual grep "
        "before treating it as an orphaned public surface (see this command's module docstring)."
    )
    return True


def unused_code(
    src: Annotated[
        Path,
        typer.Option(
            "--src",
            help="Production source directory to scan (default: the repo's src/).",
        ),
    ] = _DEFAULT_SRC_DIR,
    tests: Annotated[
        Path,
        typer.Option(
            "--tests",
            help="Test directory to scan against; only used with --test (default: the repo's tests/).",
        ),
    ] = _DEFAULT_TESTS_DIR,
    whitelist: Annotated[
        Path,
        typer.Option(
            "--whitelist",
            help="Vulture whitelist file, included in the scan if it exists; only used without --test.",
        ),
    ] = _DEFAULT_WHITELIST,
    min_confidence: Annotated[
        int,
        typer.Option(
            "--min-confidence",
            help="Vulture confidence threshold (0-100), matching the pre-commit/CI vulture hook.",
            min=0,
            max=100,
        ),
    ] = _DEFAULT_MIN_CONFIDENCE,
    test_only: Annotated[
        bool,
        typer.Option(
            "--test",
            "-t",
            help="Report symbols referenced only from --tests, never from --src itself (see module docstring).",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Exit with status 1 if any findings are reported (opt-in; off by default).",
        ),
    ] = False,
) -> None:
    """Report unused code (or, with ``--test``, code referenced only by tests).

    See this module's docstring for the full rationale and the limitations of ``--test``'s
    name-based comparison.
    """
    assert src.exists(), src
    assert tests.exists(), tests

    try:
        from vulture import Vulture  # noqa: PLC0415
    except ImportError as ex:
        typer.echo("You must install the `test` extra to run this command (`biz-dfch-specmgr[test]`).")
        raise typer.Exit(1) from ex

    if test_only:
        found = _report_test_only_usage(Vulture, src, tests, min_confidence)
    else:
        found = _report_unused_code(Vulture, src, whitelist, min_confidence)

    if found and strict:
        raise typer.Exit(1)
