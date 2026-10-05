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

"""``diagram`` -- the deterministic PlantUML diagram generation sub-command group (feat-185-uc-diagrams, Phase 130).

``specmgr diagram uc`` is the CLI half of the UC → PlantUML pipeline (plan
Overview layer 3 — thin, deterministic-only, reusing library functions, no new
logic): it writes the **deterministic** artifacts only — one
``<id>.usecase.puml`` per rendered use case plus the multi-UC
``package.puml`` over exactly the UCs of this invocation (the rulebook
``specmgr://uc/plantuml`` §2.5–§2.8 renderers, §2.10 file layout) — and with
``--check`` it regenerates those files in memory and byte-diffs them against
``--out`` without writing anything (the CI/pre-commit drift gate, REQ-009).

It never creates, overwrites, reads, or diffs ``<id>.sequence.puml``
(agent-owned — the attribution embeds agent judgment that is not
CLI-reproducible, Decisions Made 2026-10-03; the structural guard is
:func:`_assert_not_sequence_file`), and the deterministic artifacts it writes
carry no ``' validated: structure-only`` header — that is agent-path only
(REQ-005; the CLI output is checker-clean by construction, ACC-001).

Resolution and rendering are reused, not reimplemented: the disk resolution
is the Phase 120 ``get_use_case_package_diagram`` tool's own wiring (imported
**lazily** — that module registers with the MCP server, so it requires the
``mcp`` extra; the command reports the missing extra with the
``commands/mcp.py`` precedent instead of a bare ``ImportError``), and the
rendering is the pure Phase 110 ``uc.models.v2.renderer`` functions.

Exit codes (pinned, REQ-009):

* ``0`` — all artifacts written (default mode) / no diff (``--check``)
* ``1`` — a ``--check`` run found at least one differing or missing file
  (missing files count as differing), or the ``mcp`` extra is missing
* ``2`` — usage-or-render error: a wrong-format id (raised before any file
  access), an explicitly requested id that is missing on disk or exists but
  is broken (the parse error is reported — the requested artifact cannot be
  produced), a render failure, or ``all`` combined with explicit ids
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ..general.tools._doc_paths import find_parse_failure
from ..general.tools._path_safety import validate_id
from ..uc.models.v2.renderer import PackageDocument, render_uc_diagram, render_use_case_package
from ..uc.tools._cache import read_uc
from ..uc.tools._paths import uc_base_dir

__all__ = [
    "ALL_LITERAL",
    "DEFAULT_OUT_DIR",
    "PACKAGE_FILENAME",
    "diagram",
    "diagram_uc",
]

#: The sub-command group registered on the CLI app as ``diagram``.
diagram = typer.Typer(
    name="diagram",
    help="Generate (or --check) the deterministic PlantUML artifacts (feat-185-uc-diagrams).",
    no_args_is_help=True,
)

#: The default ``--out`` directory (CWD-relative, rulebook §2.10 file layout).
DEFAULT_OUT_DIR = Path("diagrams/uc")

#: The literal positional that selects every UC in ``list_uc`` order.
ALL_LITERAL = "all"

#: The fixed package-diagram filename (rulebook §2.10).
PACKAGE_FILENAME = "package.puml"

#: The agent-owned sequence-file suffix this command must never create,
#: overwrite, read, or diff (Decisions Made 2026-10-03).
_SEQUENCE_SUFFIX = ".sequence.puml"


def _usecase_filename(id_: str) -> str:
    """The per-UC artifact filename for one document id (rulebook §2.10: ``<id>.usecase.puml``)."""
    assert isinstance(id_, str), type(id_)
    assert id_, "expected a non-empty id"
    result = f"{id_}.usecase.puml"
    return result


def _assert_not_sequence_file(path: Path) -> None:
    """The structural sequence-file guard: no write or ``--check`` target may be an agent-owned ``.sequence.puml``."""
    assert isinstance(path, Path), type(path)
    assert not path.name.endswith(_SEQUENCE_SUFFIX), f"refusing to touch the agent-owned sequence file {path}"


def _resolution_helpers() -> tuple:
    """The Phase 120 tool's disk resolution, imported lazily (that module requires the ``mcp`` extra).

    Returns
    -------
    tuple
        ``(_slots_from_ids, _slots_from_listing)`` — the tool's own slot
        builders (missing/broken id ⇒ ``use_case=None`` skipped slot;
        ``ids=None`` ⇒ every UC in ``list_uc`` order, failed rows skipped).
    """
    from ..uc.tools.get_use_case_package_diagram import _slots_from_ids, _slots_from_listing  # noqa: PLC0415

    result = (_slots_from_ids, _slots_from_listing)
    return result


def _classify_skipped_slots(base_dir: Path, slots: list[PackageDocument]) -> list[str]:
    """Explicit-id mode only: every skipped slot is an error (the requested artifact cannot be produced).

    An existing-but-broken document is a **render error** (the parse error is
    reported — recovered via the shared ``find_parse_failure`` name-match, so
    a document whose filename does not carry its id in the ``create_uc``
    convention is classified as missing); a document absent on disk is a
    **usage error**. ``all`` mode never calls this — its skipped slots are the
    REQ-002 deterministic unresolvable-note path, not failures.
    """
    errors: list[str] = []
    for slot in slots:
        if slot.use_case is not None:
            continue
        assert slot.id is not None  # explicit-id mode: every slot carries the requested (validated) id
        parse_failure = find_parse_failure(base_dir, slot.id, read_uc)
        if parse_failure is not None:
            path, error = parse_failure
            errors.append(f"use case {slot.id} exists at {path} but fails to parse (render error): {error}")
        else:
            errors.append(f"no use case found with id {slot.id} (missing on disk)")
    result = errors
    return result


def diagram_uc(
    ids: Annotated[
        list[str],
        typer.Argument(help="One or more use case ids, or the literal 'all' (every UC in list_uc order)."),
    ],
    out: Annotated[
        Path,
        typer.Option(
            "--out", help="Output directory for the .puml artifacts (default: diagrams/uc/ relative to the CWD)."
        ),
    ] = DEFAULT_OUT_DIR,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Regenerate in memory and byte-diff the usecase + package files against --out (no writes): "
            "0 no diff / 1 diff found (missing files count as differing).",
        ),
    ] = False,
) -> None:
    """Write (or ``--check``) the deterministic UC → PlantUML artifacts.

    Renders one ``<id>.usecase.puml`` per given use case plus the multi-UC
    ``package.puml`` over exactly the UCs of this invocation (rulebook
    ``specmgr://uc/plantuml`` §2.5–§2.8, §2.10 file layout). ``all`` selects
    every UC in ``list_uc`` order — including ``Subfunction``-level UCs (the
    §2.11 judgment rule is agent-path only) — and skips existing-but-broken
    documents without failing the render (REQ-002: their references take the
    package's deterministic unresolvable-note path). ``--check`` regenerates
    in memory and byte-diffs the usecase + package files under ``--out``
    (missing files count as differing) without writing anything. This command
    never creates, overwrites, reads, or diffs ``<id>.sequence.puml``
    (agent-owned), and no written artifact carries the agent-path
    ``' validated: structure-only`` header (checker-clean by construction,
    REQ-005/ACC-001).

    Exit codes (pinned, REQ-009): ``0`` = all artifacts written / no diff;
    ``1`` = a ``--check`` diff found (or the ``mcp`` extra is missing);
    ``2`` = usage-or-render error (a wrong-format id — before any file
    access, an explicitly requested id that is missing on disk or exists but
    is broken — the parse error is reported, a render failure, or ``all``
    combined with explicit ids).
    """
    if ALL_LITERAL in ids and len(ids) != 1:
        typer.echo(
            f"error: the literal '{ALL_LITERAL}' selects every UC and cannot be combined with explicit ids",
            err=True,
        )
        raise typer.Exit(2)
    select_all = len(ids) == 1 and ids[0] == ALL_LITERAL

    try:
        _slots_from_ids, _slots_from_listing = _resolution_helpers()
    except ImportError as ex:
        typer.echo("You must install the `mcp` extra to use this command (`biz-dfch-specmgr[mcp]`).", err=True)
        raise typer.Exit(1) from ex

    base_dir = uc_base_dir()
    if select_all:
        slots = _slots_from_listing()
        for slot in slots:
            if slot.use_case is None:
                typer.echo(
                    "⚠ skipped an existing-but-broken document (no per-UC file; its references take the "
                    "package's deterministic note path)"
                )
    else:
        for id_ in ids:
            try:
                validate_id("uc", id_)
            except ValueError as ex:
                typer.echo(f"error: {ex}", err=True)
                raise typer.Exit(2) from ex
        slots = _slots_from_ids(ids)
        errors = _classify_skipped_slots(base_dir, slots)
        if errors:
            for error in errors:
                typer.echo(f"error: {error}", err=True)
            raise typer.Exit(2)

    artifacts: dict[str, str] = {}
    for slot in slots:
        if slot.use_case is None or slot.id is None:
            continue  # a skipped slot (all mode) or a document without a frontmatter id renders no per-UC file
        artifacts[_usecase_filename(slot.id)] = render_uc_diagram(slot.use_case)
    artifacts[PACKAGE_FILENAME] = render_use_case_package(slots)

    if check:
        differing = 0
        for name in sorted(artifacts):
            path = out / name
            _assert_not_sequence_file(path)
            if not path.is_file():
                typer.echo(f"✗ {path} (missing)")
                differing += 1
            elif path.read_text(encoding="utf-8") != artifacts[name]:
                typer.echo(f"✗ {path} (differs)")
                differing += 1
            else:
                typer.echo(f"✓ {path} (unchanged)")
        if differing:
            raise typer.Exit(1)
        return

    out.mkdir(parents=True, exist_ok=True)
    for name in sorted(artifacts):
        path = out / name
        _assert_not_sequence_file(path)
        path.write_text(artifacts[name], encoding="utf-8")
        typer.echo(f"✓ Wrote {path}")


diagram.command("uc")(diagram_uc)
