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

"""The jar/bin local validation backends (rulebook §4 — the frozen invocation contract).

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
- **Render proof:** ``--svg --no-error-image -pipe`` — exit ``0`` **and** the
  output starts with ``<svg`` ⇒ rendered; the SVG goes to a temp file (path
  optionally reported), never inlined.
- **Subprocess discipline:** list form (never a shell), path values
  charset-validated, :data:`SUBPROCESS_TIMEOUT_SECONDS` on every call.

Verified against ``plantuml/plantuml:latest`` (1.2026.8), including the
``--version`` probe. Import-free and stdlib-only (ADR 7a626b12).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .structure import Finding

__all__ = [
    "CANARY_DIAGRAM",
    "FLAG_CHECKONLY",
    "FLAG_CHECK_SYNTAX",
    "LocalVerdict",
    "ProbeResult",
    "SUBPROCESS_TIMEOUT_SECONDS",
    "clear_probe_cache",
    "probe_local",
    "scan_error_blocks",
    "validate_local",
]

#: The named subprocess timeout for every jar/bin call (rulebook §4: 60 s).
SUBPROCESS_TIMEOUT_SECONDS = 60

#: The modern check flag (auto-detected first).
FLAG_CHECK_SYNTAX = "--check-syntax"

#: The legacy check-flag fallback (builds predating ``--check-syntax``).
FLAG_CHECKONLY = "-checkonly"

#: The no-error-image flag (both check and render proof).
_FLAG_NO_ERROR_IMAGE = "--no-error-image"

#: The stdin/stdout pipe flag (no file arguments).
_FLAG_PIPE = "-pipe"

#: The render-proof output format flag.
_FLAG_SVG = "--svg"

#: The SVG magic a render-proof output must start with after any whitespace.
_SVG_MAGIC = b"<svg"

#: The canary: a known-valid mini-diagram whose round-trip proves the source
#: answers (rulebook §3.5). One check (⇒ valid) — the URL backend additionally
#: proves render.
CANARY_DIAGRAM = "@startuml\nBob -> Alice: hello\n@enduml\n"

#: The frozen ``ERROR / {line} / {message}`` text block (rulebook §4) — the
#: byte shape older builds emit.
_ERROR_SLASH_PATTERN = re.compile(rb"ERROR / (\d+) / ([^\r\n]+)")

#: The three-line byte shape 1.2026.8 actually emits (``ERROR`` / ``{line}`` /
#: ``{message}``, on stderr) — verified against the live build; the frozen
#: slash shape is retained so a build emitting either is parsed.
_ERROR_LINES_PATTERN = re.compile(rb"ERROR[ \t]*\r?\n(\d+)\r?\n([^\r\n]+)")


# --- the frozen result shapes -------------------------------------------------


@dataclass(frozen=True)
class ProbeResult:
    """The outcome of a source canary probe (rulebook §3.5).

    Attributes:
        ok: the canary round-tripped (the source answers its contract).
        source_state: ``"ok"`` / ``"misconfigured"`` (a configuration defect
            the user must fix) / ``"unavailable"`` (transient/environmental) /
            ``"inconclusive"`` — the §3.6 vocabulary, shared with the chain.
        reason: why the state is what it is (``None`` when ok).
        fix_hint: the concrete fix (``None`` when ok).
        check_flag: the resolved check flag for local sources (``None`` for a
            failed probe or the URL source).
    """

    ok: bool
    source_state: str
    reason: str | None = None
    fix_hint: str | None = None
    check_flag: str | None = None


@dataclass(frozen=True)
class LocalVerdict:
    """The outcome of a jar/bin check (+ render proof) over one diagram.

    Attributes:
        valid: the check's exit-code verdict (``0`` ⇒ ``True``).
        errors: the parsed ``ERROR`` blocks (empty when valid).
        rendered: the render-proof verdict (``None`` = not run — invalid).
        proof_path: the temp file holding the rendered SVG (``None`` when not
            rendered) — the path is reported, the bytes never inlined.
        reason: a non-None explanation when ``rendered`` is ``False``.
    """

    valid: bool
    errors: list[Finding]
    rendered: bool | None = None
    proof_path: str | None = None
    reason: str | None = None


# --- source configuration checks ----------------------------------------------


def _validate_source_value(kind: str, value: str) -> tuple[str | None, str | None]:
    """Charset/path-shape-validate a configured source value.

    Returns ``(reason, fix_hint)`` for a configuration defect, or
    ``(None, None)`` when the value is usable. A defect here is
    ``misconfigured`` (the user must fix the configuration), never a
    subprocess or network call away.
    """
    assert kind in ("jar", "bin"), kind
    if not value.strip():
        var = "SPECMGR_PLANTUML_JAR" if kind == "jar" else "SPECMGR_PLANTUML_BIN"
        return (
            f"{var} is set but empty",
            f"point {var} at an existing {'plantuml.jar path' if kind == 'jar' else 'executable'} "
            "(or unset it to select the next configured source)",
        )
    if "\0" in value:
        return (
            "the configured source path contains a NUL byte",
            "remove the NUL byte from the configured path (subprocess argv is not NUL-safe)",
        )
    try:
        value.encode("utf-8")
        Path(value).name  # resolve-ish: reject nothing, just exercise the API
    except (UnicodeEncodeError, ValueError) as exc:
        return (
            f"the configured source path is not a usable filesystem path ({type(exc).__name__})",
            "use a plain UTF-8 path for the configured source",
        )
    if kind == "jar":
        if shutil.which("java") is None:
            return (
                "java is not on PATH (the JAR source invokes 'java -jar <jar> ...')",
                "install a JDK/JRE and make sure 'java' resolves on PATH, or select a different "
                "source (SPECMGR_PLANTUML_BIN/SPECMGR_PLANTUML_URL)",
            )
        if not os.path.exists(value):
            return (
                f"SPECMGR_PLANTUML_JAR points at a path that does not exist: {value}",
                f"point SPECMGR_PLANTUML_JAR at the real plantuml.jar (e.g. a pinned download under "
                f"{Path.home()} — rulebook §7.3)",
            )
    else:
        if not os.path.exists(value):
            return (
                f"SPECMGR_PLANTUML_BIN points at a path that does not exist: {value}",
                "point SPECMGR_PLANTUML_BIN at the real executable (a distro binary or your own "
                "platform adapter — rulebook §7.1)",
            )
        if not os.access(value, os.X_OK):
            return (
                f"SPECMGR_PLANTUML_BIN is not executable: {value}",
                "make the adapter executable (chmod +x), or point SPECMGR_PLANTUML_BIN elsewhere",
            )
    return None, None


def _argv_prefix(kind: str, value: str) -> list[str]:
    """The unified invocation prefix: ``[java, -jar, <jar>]`` or ``[<bin>]``."""
    assert kind in ("jar", "bin"), kind
    if kind == "jar":
        result = ["java", "-jar", value]
    else:
        result = [value]
    return result


# --- the raw subprocess call ----------------------------------------------------


def _run(argv: list[str], stdin_data: bytes) -> tuple[int | None, bytes, bytes, str | None]:
    """Run one PlantUML subprocess call (list form, never a shell).

    Returns ``(exit_code, stdout, stderr, transport_error)`` — exactly one of
    ``exit_code`` or ``transport_error`` is set: a ``None`` exit code means
    the call never produced a verdict (spawn failure or timeout).
    """
    try:
        completed = subprocess.run(
            argv,
            input=stdin_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return None, b"", b"", f"timed out after {SUBPROCESS_TIMEOUT_SECONDS} s"
    except OSError as exc:
        return None, b"", b"", f"spawn failed ({type(exc).__name__}: {exc})"
    return completed.returncode, completed.stdout, completed.stderr, None


def scan_error_blocks(data: bytes) -> list[tuple[int, str]]:
    """Scan raw output bytes for PlantUML ``ERROR`` blocks (rulebook §4).

    Accepts both byte shapes: the frozen ``ERROR / {line} / {message}``
    one-line block and the three-line block 1.2026.8 emits
    (``ERROR`` / ``{line}`` / ``{message}``) — verified against the live
    build. Returns ``(line, message)`` pairs in order of appearance, deduped
    by (line, message); the message is decoded with ``errors="replace"``
    (the surrounding bytes can be binary-contaminated).
    """
    assert isinstance(data, bytes), type(data)
    found: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    for pattern in (_ERROR_SLASH_PATTERN, _ERROR_LINES_PATTERN):
        for match in pattern.finditer(data):
            line_number = int(match.group(1))
            message = match.group(2).decode("utf-8", errors="replace").strip()
            key = (line_number, message)
            if key not in seen:
                seen.add(key)
                found.append(key)
    found.sort(key=lambda pair: (pair[0], pair[1]))
    result = found
    return result


# --- the canary probe (memoised per process, rulebook §3.5) ----------------------

_PROBE_CACHE: dict[tuple[str, str], ProbeResult] = {}


def clear_probe_cache() -> None:
    """Drop every memoised canary probe result (test hook — never called from src/)."""
    _PROBE_CACHE.clear()


def _run_check(argv_prefix: list[str], check_flag: str, diagram: str) -> tuple[int | None, bytes, bytes, str | None]:
    """One check call: ``<prefix> <flag> --no-error-image -pipe`` with the diagram on stdin."""
    argv = [*argv_prefix, check_flag, _FLAG_NO_ERROR_IMAGE, _FLAG_PIPE]
    return _run(argv, diagram.encode("utf-8"))


def probe_local(kind: str, value: str) -> ProbeResult:
    """Probe a jar/bin source with the canary (rulebook §3.5 + §4 flag auto-detect).

    The probe is memoised per process per ``(kind, value)`` — the agent's
    validate loop never re-probes. The canary round-trip doubles as the flag
    probe: a build answering ``--check-syntax`` keeps it; a build whose
    canary fails with that flag is retried once with the legacy
    ``-checkonly`` flag (unknown options are ignored by the parser, so a
    failing canary means the build genuinely cannot check).

    A configuration defect (bad path, missing java, not executable) is
    ``misconfigured`` and is decided **without** any subprocess; a reachable
    source that fails the canary round-trip is ``unavailable``.
    """
    assert kind in ("jar", "bin"), kind
    assert isinstance(value, str), type(value)
    cache_key = (kind, value)
    if cache_key in _PROBE_CACHE:
        result = _PROBE_CACHE[cache_key]
        return result

    reason, fix_hint = _validate_source_value(kind, value)
    if reason is not None:
        result = ProbeResult(ok=False, source_state="misconfigured", reason=reason, fix_hint=fix_hint)
        _PROBE_CACHE[cache_key] = result
        return result

    argv_prefix = _argv_prefix(kind, value)
    last_error: str | None = None
    for check_flag in (FLAG_CHECK_SYNTAX, FLAG_CHECKONLY):
        exit_code, out, err, transport_error = _run_check(argv_prefix, check_flag, CANARY_DIAGRAM)
        if transport_error is not None:
            last_error = transport_error
            continue
        if exit_code == 0:
            result = ProbeResult(ok=True, source_state="ok", check_flag=check_flag)
            _PROBE_CACHE[cache_key] = result
            return result
        blocks = scan_error_blocks(out + b"\n" + err)
        if blocks:
            last_error = f"the canary diagram was rejected: {blocks[0][1]} (line {blocks[0][0]}, exit {exit_code})"
        else:
            stderr_tail = err.decode("utf-8", errors="replace").strip()[-200:]
            last_error = f"the canary check exited {exit_code} without a parseable ERROR block"
            if stderr_tail:
                last_error += f" (stderr tail: {stderr_tail!r})"
    result = ProbeResult(
        ok=False,
        source_state="unavailable",
        reason=f"the canary round-trip through the {kind} source failed: {last_error}",
        fix_hint="point the variable at an executable that speaks the PlantUML -pipe check contract "
        "(rulebook §4) — e.g. a pinned plantuml.jar behind SPECMGR_PLANTUML_JAR or a docker CLI "
        "container adapter behind SPECMGR_PLANTUML_BIN (rulebook §7.1)",
    )
    _PROBE_CACHE[cache_key] = result
    return result


# --- the real check + render proof ----------------------------------------------


def _write_proof(svg_bytes: bytes) -> str:
    """Write a render-proof SVG to a temp file; return its path (never inlined)."""
    handle = tempfile.NamedTemporaryFile(prefix="plantuml-proof-", suffix=".svg", delete=False)
    with handle:
        handle.write(svg_bytes)
    result = handle.name
    return result


def validate_local(kind: str, value: str, diagram: str, check_flag: str) -> LocalVerdict:
    """Run the check (and, when valid, the render proof) over ``diagram``.

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
    """
    assert kind in ("jar", "bin"), kind
    assert isinstance(diagram, str), type(diagram)
    assert check_flag in (FLAG_CHECK_SYNTAX, FLAG_CHECKONLY), check_flag

    argv_prefix = _argv_prefix(kind, value)
    exit_code, out, err, transport_error = _run_check(argv_prefix, check_flag, diagram)
    if transport_error is not None:
        result = LocalVerdict(
            valid=False,
            errors=[
                Finding(
                    0,
                    f"the {kind} check could not be run: {transport_error}",
                    "check the source configuration (rulebook §3.1) and retry",
                )
            ],
        )
        return result

    if exit_code != 0:
        blocks = scan_error_blocks(out + b"\n" + err)
        if blocks:
            errors = [
                Finding(
                    line,
                    f"syntax error reported by PlantUML: {message}",
                    "fix the syntax error at the reported line of the diagram source",
                )
                for line, message in blocks
            ]
        else:
            errors = [
                Finding(
                    0,
                    f"the PlantUML check exited {exit_code} without a parseable ERROR block",
                    "re-run with a local jar/bin source for the parser's own error text, or inspect "
                    "the diagram by hand (rulebook §4)",
                )
            ]
        result = LocalVerdict(valid=False, errors=errors)
        return result

    # valid: the render proof — exit 0 AND the output starts with <svg (rulebook §4)
    render_argv = [*argv_prefix, _FLAG_SVG, _FLAG_NO_ERROR_IMAGE, _FLAG_PIPE]
    render_code, svg_out, svg_err, render_error = _run(render_argv, diagram.encode("utf-8"))
    if render_error is not None:
        result = LocalVerdict(
            valid=True,
            errors=[],
            rendered=False,
            reason=f"the render proof could not be run: {render_error}",
        )
    elif render_code == 0 and svg_out.lstrip().startswith(_SVG_MAGIC):
        result = LocalVerdict(
            valid=True,
            errors=[],
            rendered=True,
            proof_path=_write_proof(svg_out),
        )
    else:
        stderr_tail = svg_err.decode("utf-8", errors="replace").strip()[-200:]
        detail = f"exit {render_code}" if render_code != 0 else "output does not start with '<svg'"
        if stderr_tail:
            detail += f" (stderr tail: {stderr_tail!r})"
        result = LocalVerdict(
            valid=True,
            errors=[],
            rendered=False,
            reason=f"the render proof failed: {detail}",
        )
    return result
