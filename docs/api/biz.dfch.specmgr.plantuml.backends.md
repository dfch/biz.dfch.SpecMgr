# `biz.dfch.specmgr.plantuml.backends`

The jar/bin local validation backends (rulebook §4 — the frozen invocation contract).

One unified invocation shape for both source kinds — all diagram content via
stdin, all output on stdout/stderr (no file arguments, no container volume
mapping needed):

- **Check:** ``--check-syntax --no-error-image -pipe`` (flag fallback
  ``-checkonly`` for builds predating ``--check-syntax`` — auto-detected with
  the canary, memoised).
- **Verdict = the exit code:** ``0`` = valid; any non-zero = invalid (current
  releases report ``200`` on a syntax error, legacy builds ``-1``). The error
  message is parsed from the **raw byte stream** — stdout is
  binary-contaminated (a placeholder PNG is emitted even for *valid* ``-pipe``
  checks), so both streams are scanned as bytes.
- **Error message shape:** the ``ERROR / {line} / {message}`` text block —
  1.2026.8 emits it as three lines (``ERROR`` / ``{line}`` / ``{message}``)
  on stderr; both byte shapes are scanned (see :func:`scan_error_blocks`).
- **Crash signature (rulebook §5.2 crash line, verified 2026-10-06):** a
  non-zero exit **without** a parseable ``ERROR`` block whose raw byte
  stream carries a PlantUML server-side crash (the known 1.2026.8
  self-message/note-left shape bug — ``ClassCastException`` on stderr, exit
  200) is the same crash diagnostic as the URL crash page: ``valid=False``
  with a line-0 finding carrying the crash exception class (see
  :func:`scan_crash`).
- **Render proof:** ``--svg --no-error-image -pipe`` — exit ``0`` **and** the
  output starts with ``<svg`` ⇒ rendered; the SVG goes to a temp file (path
  optionally reported), never inlined.
- **Subprocess discipline:** list form (never a shell), path values
  charset-validated, :data:`SUBPROCESS_TIMEOUT_SECONDS` on every call.

Verified against ``plantuml/plantuml:latest`` (1.2026.8), including the
``--version`` probe. Import-free and stdlib-only (ADR 7a626b12).

## Classes

### `LocalVerdict`

The outcome of a jar/bin check (+ render proof) over one diagram.

Attributes:
    valid: the check's exit-code verdict (``0`` ⇒ ``True``).
    errors: the parsed ``ERROR`` blocks, or the crash diagnostic (the
        rulebook §5.2 crash line — a non-zero exit without a parseable
        ``ERROR`` block but with the crash signature in the raw stream)
        or the generic no-block finding (empty when valid).
    rendered: the render-proof verdict (``None`` = not run — invalid).
    proof_path: the temp file holding the rendered SVG (``None`` when not
        rendered) — the path is reported, the bytes never inlined.
    reason: a non-None explanation when ``rendered`` is ``False``.


### `ProbeResult`

The outcome of a source canary probe (rulebook §3.5).

Attributes:
    ok: the canary round-tripped (the source answers its contract).
    source_state: ``"ok"`` / ``"misconfigured"`` (a configuration defect
        the user must fix) / ``"unavailable"`` (transient/environmental) /
        ``"inconclusive"`` — the §3.6 vocabulary, shared with the chain.
    reason: why the state is what it is (``None`` when ok).
    fix_hint: the concrete fix (``None`` when ok).
    check_flag: the resolved check flag for local sources (``None`` for a
        failed probe or the URL source).


## Functions

### `_argv_prefix(kind: 'str', value: 'str') -> 'list[str]'`

The unified invocation prefix: ``[java, -jar, <jar>]`` or ``[<bin>]``.


### `_run(argv: 'list[str]', stdin_data: 'bytes') -> 'tuple[int | None, bytes, bytes, str | None]'`

Run one PlantUML subprocess call (list form, never a shell).

Returns ``(exit_code, stdout, stderr, transport_error)`` — exactly one of
``exit_code`` or ``transport_error`` is set: a ``None`` exit code means
the call never produced a verdict (spawn failure or timeout).


### `_run_check(argv_prefix: 'list[str]', check_flag: 'str', diagram: 'str') -> 'tuple[int | None, bytes, bytes, str | None]'`

One check call: ``<prefix> <flag> --no-error-image -pipe`` with the diagram on stdin.


### `_validate_source_value(kind: 'str', value: 'str') -> 'tuple[str | None, str | None]'`

Charset/path-shape-validate a configured source value.

Returns ``(reason, fix_hint)`` for a configuration defect, or
``(None, None)`` when the value is usable. A defect here is
``misconfigured`` (the user must fix the configuration), never a
subprocess or network call away.


### `_write_proof(svg_bytes: 'bytes') -> 'str'`

Write a render-proof SVG to a temp file; return its path (never inlined).


### `clear_probe_cache() -> 'None'`

Drop every memoised canary probe result (test hook — never called from src/).


### `probe_local(kind: 'str', value: 'str') -> 'ProbeResult'`

Probe a jar/bin source with the canary (rulebook §3.5 + §4 flag auto-detect).

The probe is memoised per process per ``(kind, value)`` — the agent's
validate loop never re-probes. A FAILURE outcome (``misconfigured`` /
``unavailable``) is memoised for the process lifetime exactly like a
success — a long-lived MCP server therefore keeps a stale failure after
the configuration is fixed (a JDK installed, a path corrected) until it
is restarted, or the probe cache is cleared (rulebook §3.5, operator
note 2026-10-08). The canary round-trip doubles as the flag probe: a
build answering ``--check-syntax`` keeps it; a build whose canary fails
with that flag is retried once with the legacy ``-checkonly`` flag
(unknown options are ignored by the parser, so a failing canary means
the build genuinely cannot check). Auto-detect caveat (2026-10-08):
that assumption is verified for current builds (rulebook §4: 1.2026.8)
— a pre-``--check-syntax`` legacy build that RENDERS on the unrecognised
flag (exit 0) would make the probe select "check" on a build that
treats it as render; such legacy builds are out of support scope.

A configuration defect (bad path, missing java, not executable) is
``misconfigured`` and is decided **without** any subprocess; a reachable
source that fails the canary round-trip is ``unavailable``.


### `scan_crash(data: 'bytes') -> 'str | None'`

The fully-qualified crash exception class name in ``data``, or ``None``.

The rulebook §5.2 crash line (verified 2026-10-06 on both independent
sources — the dev jetty 1.2026.8 and the same-build jar): a PlantUML
server-side crash is a **recognised** signature, never a transport or
configuration issue. Two byte shapes carry it: the URL crash page (the
:data:`CRASH_PAGE_MARKER` sentence + the embedded Java exception trace)
and the jar/bin raw process stream (the :data:`CRASH_EXCEPTION_MARKER`
trace on stderr — the known 1.2026.8 self-message/note-left shape bug,
exit 200 with no parseable ``ERROR`` block). The returned name (e.g.
``java.lang.ClassCastException``) goes into the crash diagnostic's
finding; ``None`` = no crash signature, whatever else the bytes carry.


### `scan_error_blocks(data: 'bytes') -> 'list[tuple[int, str]]'`

Scan raw output bytes for PlantUML ``ERROR`` blocks (rulebook §4).

Accepts both byte shapes: the frozen ``ERROR / {line} / {message}``
one-line block and the three-line block 1.2026.8 emits
(``ERROR`` / ``{line}`` / ``{message}``) — verified against the live
build. Returns ``(line, message)`` pairs sorted by ``(line, message)``,
deduped by (line, message); the message is decoded with ``errors="replace"``
(the surrounding bytes can be binary-contaminated).


### `validate_local(kind: 'str', value: 'str', diagram: 'str', check_flag: 'str') -> 'LocalVerdict'`

Run the check (and, when valid, the render proof) over ``diagram``.

Parameters
----------
kind:
    ``"jar"`` or ``"bin"`` — the selected source kind.
value:
    The configured source value (the jar path / the executable path).
diagram:
    The full diagram source (stdin).
check_flag:
    The resolved check flag from :func:`probe_local` (``--check-syntax``
    or ``-checkonly``).

Returns
-------
LocalVerdict
    The exit-code verdict with the parsed ``ERROR`` blocks; when valid,
    the render proof (``--svg`` to a temp file) as well.

