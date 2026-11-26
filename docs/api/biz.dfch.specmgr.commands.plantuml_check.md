# `biz.dfch.specmgr.commands.plantuml_check`

``plantuml-check`` -- validate any ``.puml`` file(s) through the strict chain (feat-185-uc-diagrams, Phase 130).

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

## Functions

### `_bool_word(value: 'bool | None') -> 'str'`

The verdict word for one ``valid``/``rendered`` field (``None`` = not run, rulebook §3.6).


### `_file_exit_code(result: 'PlantumlValidationResult') -> 'int'`

Map one file's §3.6 result to this command's pinned exit code (the module docstring's table).


### `_print_finding(path_str: 'str', finding: 'Finding', *, warning: 'bool') -> 'None'`

One finding line: ``{path}:{line}: {message} (fix: {fix_hint})`` (feat-27 convention).


### `_print_verdict(path_str: 'str', result: 'PlantumlValidationResult') -> 'None'`

The per-file verdict block (the console contract in the module docstring).


### `plantuml_check(paths: "Annotated[list[str], typer.Argument(help='One or more .puml files to validate (agent-owned sequence files included).')]") -> 'None'`

Validate one or more ``.puml`` files through the strict chain (rulebook §3).

Every path must be a readable ``.puml`` file (a non-``.puml`` or
missing/unreadable path is a usage error — exit 2, all problems of the
invocation reported before any chain run). Each file's text goes through
``plantuml.chain.validate_plantuml``; the per-file verdict and findings
are printed (see the module docstring), and the invocation exits with
the worst applicable code by the pinned severity order
``2 > 3 > 1 > 0``.

