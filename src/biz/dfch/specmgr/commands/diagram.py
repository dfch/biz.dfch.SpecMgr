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

"""``diagram`` -- the deterministic PlantUML diagram commands (feat-185-uc-diagrams; feat-207-reference-graph).

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

``specmgr diagram refs`` (feat-207-reference-graph, Phase 130) is the CLI
half of the reference-graph pipeline, the same thin layer: ``refs <type>
<id>`` writes the scoped neighbourhood graph of one source document to
``<id>.refs.puml`` (the literal ``refs all`` writes the registry-wide graph
to ``reference-graph.puml``), and with ``--check`` it regenerates the file
in memory and byte-diffs it against ``--out`` without writing anything
(rulebook ``specmgr://reference-graph`` §2–§5 emission, §7 file layout; the
CI/pre-commit drift gate, REQ-009). The command is thin over the Phase 120
tools ``get_reference_diagram`` / ``get_reference_diagram_all`` (imported
**lazily** — they register with the MCP server, so they require the ``mcp``
extra; the same missing-extra report as ``uc``): their own guard order
(Design Notes §7 — ``validate_id`` and the ``depth`` 1..5 check both before
any filesystem access, the source domain's own ``XNotFoundError`` for a
missing source, the non-raising ``ParseFailureResult`` for an
existing-but-broken source) maps straight onto this command's exit-2
channel, and the Phase 110 shared helper reads ``SPECMGR_DIAGRAM_MAX_TITLE``
(default 40) for the resolved-node label limit. For ``type="feat"`` the full
``feat-NNN-slug`` is the only accepted source id (a bare ``feat-NNN`` is
rejected — use ``list_feat`` to discover the exact id). The written
artifacts carry no ``' validated: structure-only`` header (checker-clean by
construction; run ``specmgr plantuml-check`` on them for a verdict).

Exit codes (pinned, REQ-009 — the same contract for both members):

* ``0`` — the artifact(s) written (default mode) / no diff (``--check``)
* ``1`` — a ``--check`` run found at least one differing or missing file
  (missing files count as differing), or the ``mcp`` extra is missing
* ``2`` — usage-or-resolution error: a wrong-format id / type / depth
  (raised before any file access), an explicitly requested source that is
  missing on disk or exists but is broken (the parse error is reported —
  the requested artifact cannot be produced), a render failure, or ``all``
  combined with explicit ids (``uc``) / a source id (``refs``)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ..general.models import ParseFailureResult
from ..general.tools._doc_paths import find_parse_failure
from ..general.tools._path_safety import validate_id
from ..uc.models.v2.renderer import PackageDocument, render_uc_diagram, render_use_case_package
from ..uc.tools._cache import read_uc
from ..uc.tools._paths import uc_base_dir

__all__ = [
    "ALL_LITERAL",
    "DEFAULT_OUT_DIR",
    "DEFAULT_REFS_OUT_DIR",
    "PACKAGE_FILENAME",
    "REGISTRY_REFS_FILENAME",
    "diagram",
    "diagram_refs",
    "diagram_uc",
]

#: The sub-command group registered on the CLI app as ``diagram``.
diagram = typer.Typer(
    name="diagram",
    help="Generate (or --check) the deterministic PlantUML artifacts (UC diagrams, reference graphs).",
    no_args_is_help=True,
)

#: The default ``--out`` directory (CWD-relative, rulebook §2.10 file layout).
DEFAULT_OUT_DIR = Path("diagrams/uc")

#: The literal positional that selects every UC in ``list_uc`` order.
ALL_LITERAL = "all"

#: The fixed package-diagram filename (rulebook §2.10).
PACKAGE_FILENAME = "package.puml"

#: The default ``--out`` directory for the reference-graph member (CWD-relative,
#: rulebook ``specmgr://reference-graph`` §7 file layout).
DEFAULT_REFS_OUT_DIR = Path("diagrams/refs")

#: The fixed registry-wide reference-graph filename (rulebook §7).
REGISTRY_REFS_FILENAME = "reference-graph.puml"

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


def _reference_graph_tools() -> tuple:
    """The Phase 120 reference-graph tools, imported lazily (those modules register with the MCP
    server, so they require the ``mcp`` extra).

    Returns
    -------
    tuple
        ``(get_reference_diagram, get_reference_diagram_all)`` — the tools'
        own guard order (``validate_id`` + the ``depth`` 1..5 range check,
        both before any filesystem access; the source domain's own
        ``XNotFoundError`` for a missing source; the non-raising
        ``ParseFailureResult`` for an existing-but-broken source) is what
        the ``refs`` member maps onto its exit codes.
    """
    from ..general.tools.get_reference_diagram import get_reference_diagram  # noqa: PLC0415
    from ..general.tools.get_reference_diagram_all import get_reference_diagram_all  # noqa: PLC0415

    result = (get_reference_diagram, get_reference_diagram_all)
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
                # name the skipped document (the 2026-10-08 actionable-warning fix):
                # the id when present, else the resolved path — a list_uc failed
                # row's id is None (the frontmatter is unreadable), its path is not
                if slot.id is not None:
                    identifier = f"(id: {slot.id})"
                elif slot.path is not None:
                    identifier = f"(path: {slot.path})"
                else:
                    identifier = "(unknown document)"
                typer.echo(
                    f"⚠ skipped an existing-but-broken document {identifier} — no per-UC file; its "
                    "references take the package's deterministic note path"
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


def diagram_refs(  # pylint: disable=redefined-builtin  # type/id intentionally shadow the builtins: public CLI API (issue #41)
    type: Annotated[
        str,
        typer.Argument(
            help="The source document's domain (one of adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, "
            "feat, vcr, sysrs), or the literal 'all' for the registry-wide graph.",
        ),
    ],
    id: Annotated[
        str | None,
        typer.Argument(
            help="The source document's id (required unless the type is 'all'; for feat the full "
            "feat-NNN-slug — use list_feat to discover the exact id).",
        ),
    ] = None,
    depth: Annotated[
        int,
        typer.Option(
            "--depth",
            help="The forward BFS depth: 1..5 (default: 1). Scoped mode only; --reverse is additive "
            "and direct-only on the incoming side.",
        ),
    ] = 1,
    reverse: Annotated[
        bool,
        typer.Option(
            "--reverse",
            help="Also add the direct incoming references to the source (additive; --depth governs "
            "the forward part only). Scoped mode only.",
        ),
    ] = False,
    no_feat: Annotated[
        bool,
        typer.Option(
            "--no-feat",
            help="Exclude FEAT artifacts: drop every FEAT node except the explicitly requested source "
            "(scoped mode), then drop every edge touching a dropped node.",
        ),
    ] = False,
    title: Annotated[
        str | None,
        typer.Option(
            "--title",
            help="Override the diagram title (default: the source's H1 in scoped mode, 'Reference "
            "Graph' for 'all'; sanitized but never truncated).",
        ),
    ] = None,
    out: Annotated[
        Path,
        typer.Option(
            "--out", help="Output directory for the .puml artifact (default: diagrams/refs/ relative to the CWD)."
        ),
    ] = DEFAULT_REFS_OUT_DIR,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Regenerate in memory and byte-diff the .puml file against --out (no writes): "
            "0 no diff / 1 diff found (a missing file counts as differing).",
        ),
    ] = False,
) -> None:
    """Write (or ``--check``) the deterministic reference-graph PlantUML diagram.

    ``refs <type> <id>`` renders the scoped graph of one source document —
    the source itself (level 0), its outgoing references walked to
    ``--depth`` (1..5, default 1), and with ``--reverse`` the direct
    incoming references to the source (additive, direct-only on the
    incoming side) — to ``<id>.refs.puml``; the literal ``refs all``
    renders the registry-wide graph to ``reference-graph.puml`` (rulebook
    ``specmgr://reference-graph`` §2–§5 emission, §7 file layout). This
    command is thin over the Phase 120 tools ``get_reference_diagram`` /
    ``get_reference_diagram_all``: the same guard order, the same builders,
    the same byte-stable renderer — resolved-node labels truncated to the
    ``SPECMGR_DIAGRAM_MAX_TITLE`` env var (default 40), the diagram title
    sanitized but never truncated. For ``type="feat"`` the full
    ``feat-NNN-slug`` is the only accepted id (a bare ``feat-NNN`` is
    rejected — use ``list_feat`` to discover the exact id).

    ``--check`` regenerates the file in memory and byte-diffs it against
    ``--out`` (a missing file counts as differing) without writing
    anything. No written artifact carries the agent-path
    ``' validated: structure-only`` header (checker-clean by
    construction) — run ``specmgr plantuml-check`` on the files for a
    validation verdict.

    Exit codes (pinned, REQ-009): ``0`` = written / no diff; ``1`` = a
    ``--check`` diff found (a missing file included) or the ``mcp`` extra
    is missing; ``2`` = usage-or-resolution error (a wrong-format
    ``type``/``id``/``depth`` — before any file access, a missing source,
    an existing-but-broken source — the parse error is reported, ``all``
    combined with a source id, or ``refs <type>`` without an id).
    """
    # Usage errors first (the ``diagram uc`` order: before the lazy import
    # and before any filesystem access): 'all' selects the registry-wide
    # graph on its own; a scoped call needs both a type and an id.
    select_all = type == ALL_LITERAL
    if select_all and id is not None:
        typer.echo(
            f"error: the literal '{ALL_LITERAL}' selects the registry-wide graph and cannot be combined with a source",
            err=True,
        )
        raise typer.Exit(2)
    if not select_all and id is None:
        typer.echo("error: a source id is required (the literal 'all' selects the registry-wide graph)", err=True)
        raise typer.Exit(2)

    try:
        get_diagram, get_diagram_all = _reference_graph_tools()
    except ImportError as ex:
        typer.echo("You must install the `mcp` extra to use this command (`biz-dfch-specmgr[mcp]`).", err=True)
        raise typer.Exit(1) from ex

    if select_all:
        # The registry-wide tool: no id guards, never raises for content.
        diagram_text: str = get_diagram_all(include_feat=not no_feat, title=title)
    else:
        assert id is not None  # the usage-error check above raised for (scoped, id is None)
        # The scoped tool's own guard order (Design Notes §7) maps straight
        # onto this command's exit-2 channel: ValueError for a wrong-format
        # type/id/depth (before any filesystem access), the source domain's
        # own XNotFoundError (a LookupError subclass) for a missing source,
        # and the non-raising ParseFailureResult for an existing-but-broken
        # source (the CLI has no non-raising return concept — the parse
        # error is reported, the ``diagram uc`` render-error shape).
        try:
            outcome = get_diagram(
                type=type,
                id=id,
                depth=depth,
                reverse=reverse,
                include_feat=not no_feat,
                title=title,
            )
        except ValueError as ex:
            typer.echo(f"error: {ex}", err=True)
            raise typer.Exit(2) from ex
        except LookupError as ex:
            typer.echo(f"error: {ex}", err=True)
            raise typer.Exit(2) from ex
        if isinstance(outcome, ParseFailureResult):
            typer.echo(
                f"error: {type} document {outcome.id} exists at {outcome.path} but fails to parse "
                f"(render error): {outcome.error}",
                err=True,
            )
            raise typer.Exit(2)
        diagram_text = outcome

    filename = REGISTRY_REFS_FILENAME if select_all else f"{id}.refs.puml"
    path = out / filename
    if check:
        if not path.is_file():
            typer.echo(f"✗ {path} (missing)")
            raise typer.Exit(1)
        if path.read_text(encoding="utf-8") != diagram_text:
            typer.echo(f"✗ {path} (differs)")
            raise typer.Exit(1)
        typer.echo(f"✓ {path} (unchanged)")
        return

    out.mkdir(parents=True, exist_ok=True)
    path.write_text(diagram_text, encoding="utf-8")
    typer.echo(f"✓ Wrote {path}")


diagram.command("refs")(diagram_refs)
