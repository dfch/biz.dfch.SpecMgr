# `biz.dfch.specmgr.commands.diagram`

``diagram`` -- the deterministic PlantUML diagram generation sub-command group (feat-185-uc-diagrams, Phase 130).

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

