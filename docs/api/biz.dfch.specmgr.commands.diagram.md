# `biz.dfch.specmgr.commands.diagram`

``diagram`` -- the deterministic PlantUML diagram commands (feat-185-uc-diagrams; feat-207-reference-graph).

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

## Functions

### `_assert_not_sequence_file(path: 'Path') -> 'None'`

The structural sequence-file guard: no write or ``--check`` target may be an agent-owned ``.sequence.puml``.


### `_classify_skipped_slots(base_dir: 'Path', slots: 'list[PackageDocument]') -> 'list[str]'`

Explicit-id mode only: every skipped slot is an error (the requested artifact cannot be produced).

An existing-but-broken document is a **render error** (the parse error is
reported — recovered via the shared ``find_parse_failure`` name-match, so
a document whose filename does not carry its id in the ``create_uc``
convention is classified as missing); a document absent on disk is a
**usage error**. ``all`` mode never calls this — its skipped slots are the
REQ-002 deterministic unresolvable-note path, not failures.


### `_reference_graph_tools() -> 'tuple'`

The Phase 120 reference-graph tools, imported lazily (those modules register with the MCP
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


### `_resolution_helpers() -> 'tuple'`

The Phase 120 tool's disk resolution, imported lazily (that module requires the ``mcp`` extra).

Returns
-------
tuple
    ``(_slots_from_ids, _slots_from_listing)`` — the tool's own slot
    builders (missing/broken id ⇒ ``use_case=None`` skipped slot;
    ``ids=None`` ⇒ every UC in ``list_uc`` order, failed rows skipped).


### `_usecase_filename(id_: 'str') -> 'str'`

The per-UC artifact filename for one document id (rulebook §2.10: ``<id>.usecase.puml``).


### `diagram_refs(type: 'Annotated[str, typer.Argument(help="The source document\'s domain (one of adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt), or the literal \'all\' for the registry-wide graph.")]', id: 'Annotated[str | None, typer.Argument(help="The source document\'s id (required unless the type is \'all\'; for feat the full feat-NNN-slug — use list_feat to discover the exact id).")]' = None, depth: "Annotated[int, typer.Option('--depth', help='The forward BFS depth: 1..5 (default: 1). Scoped mode only; --reverse is additive and direct-only on the incoming side.')]" = 1, reverse: "Annotated[bool, typer.Option('--reverse', help='Also add the direct incoming references to the source (additive; --depth governs the forward part only). Scoped mode only.')]" = False, no_feat: "Annotated[bool, typer.Option('--no-feat', help='Exclude FEAT artifacts: drop every FEAT node except the explicitly requested source (scoped mode), then drop every edge touching a dropped node.')]" = False, title: 'Annotated[str | None, typer.Option(\'--title\', help="Override the diagram title (default: the source\'s H1 in scoped mode, \'Reference Graph\' for \'all\'; sanitized but never truncated).")]' = None, out: "Annotated[Path, typer.Option('--out', help='Output directory for the .puml artifact (default: diagrams/refs/ relative to the CWD).')]" = PosixPath('/refs'), check: "Annotated[bool, typer.Option('--check', help='Regenerate in memory and byte-diff the .puml file against --out (no writes): 0 no diff / 1 diff found (a missing file counts as differing).')]" = False) -> 'None'`

Write (or ``--check``) the deterministic reference-graph PlantUML diagram.

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


### `diagram_uc(ids: 'Annotated[list[str], typer.Argument(help="One or more use case ids, or the literal \'all\' (every UC in list_uc order).")]', out: "Annotated[Path, typer.Option('--out', help='Output directory for the .puml artifacts (default: diagrams/uc/ relative to the CWD).')]" = PosixPath('/uc'), check: "Annotated[bool, typer.Option('--check', help='Regenerate in memory and byte-diff the usecase + package files against --out (no writes): 0 no diff / 1 diff found (missing files count as differing).')]" = False) -> 'None'`

Write (or ``--check``) the deterministic UC → PlantUML artifacts.

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

