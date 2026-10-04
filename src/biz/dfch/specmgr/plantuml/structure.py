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

"""The two-mode PlantUML structure checker (rulebook §6) + the shared UNATTRIBUTED marker constant.

A line-oriented subset linter — **not** a grammar engine. It lints exactly the
subset of PlantUML the specmgr renderers emit (plus the agent's attributed
sequence files): ``@startuml``/``@enduml`` presence, actor/participant/usecase
declarations (quoted or bare labels, ``as`` aliases, ``<<stereotypes>>``),
usecase associations (``-->``), package edges (``..>``), sequence messages
(``->``/``-->``/self), note blocks, the fragment stack (``alt``/``opt``/
``loop``/``group``/``box``/``rectangle``/``package`` with ``end``), quote
sanitisation (the ``#quot;`` convention), and ``'`` comment lines — including
UNATTRIBUTED-marker detection.

Every finding carries a **1-based line number + cause + fix hint** (the
feat-27 actionable-error convention). Findings split into ``errors`` and
``warnings`` by mode:

- :data:`MODE_PREFLIGHT` — an authoritative validation source is available:
  the verified parser-lenient set (:data:`_LENIENT` findings) is reported as
  warnings (non-blocking).
- :data:`MODE_STANDALONE` — no source is configured: the same set is promoted
  to errors.

The checker **never rejects what the real parser accepts**: every lenient case
was verified to render OK against the real parser (rulebook §6.4 — the exact
five: unclosed fragment at EOF, missing ``@enduml``, bare ``@end``, dangling
arrow, undeclared participant in a sequence message). A missing
``@startuml`` is an error in **both** modes (the server classifies such
payloads as nothing-extractable). UNATTRIBUTED markers are warnings in both
modes (deliberate placeholders — syntactically ``'`` comments the real parser
accepts; the zero-marker rule is enforced by the agent flow, not here).

Import-free and stdlib-only (ADR 7a626b12): no specmgr imports. The
UNATTRIBUTED marker prefix lives here as ONE shared constant used by both the
renderer (``uc/models/v2/renderer.py``) and this checker, so the two cannot
drift (rulebook §2.9.4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "MODE_PREFLIGHT",
    "MODE_STANDALONE",
    "Finding",
    "StructureCheckResult",
    "UNATTRIBUTED_MARKER_PREFIX",
    "check_structure",
    "is_unattributed_marker",
    "unattributed_ext_marker",
    "unattributed_step_marker",
    "unattributed_trigger_marker",
]

# --- modes (rulebook §6.3) ----------------------------------------------------

#: Preflight mode: an authoritative source is available — the verified
#: parser-lenient set is reported as warnings (non-blocking).
MODE_PREFLIGHT = "preflight"

#: Standalone mode: no source is configured — the lenient set is promoted to
#: errors.
MODE_STANDALONE = "standalone"

_MODES = (MODE_PREFLIGHT, MODE_STANDALONE)

# --- the shared UNATTRIBUTED marker (rulebook §2.9.4) -------------------------

#: The ONE shared marker prefix (frozen grammar): a message the skeleton could
#: not attribute deterministically is emitted as a ``'`` comment line starting
#: with this prefix instead of an arrow. Used by the renderer (to emit) and by
#: :func:`check_structure` (to detect), so the two cannot drift.
UNATTRIBUTED_MARKER_PREFIX = "' UNATTRIBUTED "

#: The three frozen marker forms (the rulebook §2.9.4 grammar), for
#: documentation and test pinning:
#:
#: - ``' UNATTRIBUTED step {N}: <text>`` — a main-scenario step
#: - ``' UNATTRIBUTED ext {N}{a} step {M}: <text>`` — an extension item
#: - ``' UNATTRIBUTED trigger: <text>`` — the trigger (virtual step 0)
UNATTRIBUTED_MARKER_FORMS = (
    "' UNATTRIBUTED step {N}: <text>",
    "' UNATTRIBUTED ext {N}{a} step {M}: <text>",
    "' UNATTRIBUTED trigger: <text>",
)

_UNATTRIBUTED_MARKER_PATTERN = re.compile(r"^' UNATTRIBUTED (?:step \d+: |ext \d+[a-z]? step \d+: |trigger: )")


def is_unattributed_marker(line: str) -> bool:
    """Return ``True`` if ``line`` is an UNATTRIBUTED marker comment line.

    Detection is by the shared :data:`UNATTRIBUTED_MARKER_PREFIX` plus the
    frozen grammar tail (one of the three forms); a comment line carrying the
    prefix but a malformed tail still matches (the checker warns on any
    ``' UNATTRIBUTED ``-led line — the agent flow owns the zero-marker rule).
    """
    assert isinstance(line, str), type(line)
    return line.startswith(UNATTRIBUTED_MARKER_PREFIX)


def unattributed_step_marker(step: int, text: str) -> str:
    """Build the main-step marker form: ``' UNATTRIBUTED step {N}: <text>``.

    ``step`` is the 1-based step ordinal; ``text`` the message text
    (single-line-escaped by the caller per rulebook §2.4 — a marker is one
    PlantUML line).
    """
    assert isinstance(step, int) and step >= 1, step
    assert isinstance(text, str), type(text)
    result = f"{UNATTRIBUTED_MARKER_PREFIX}step {step}: {text}"
    return result


def unattributed_ext_marker(extension_ref: str, item: int, text: str) -> str:
    """Build the extension-item marker form: ``' UNATTRIBUTED ext {N}{a} step {M}: <text>``.

    ``extension_ref`` is the extension's anchored reference with its optional
    letter concatenated (e.g. ``"3a"``); ``item`` the 1-based item ordinal
    within the extension; ``text`` as in :func:`unattributed_step_marker`.
    """
    assert isinstance(extension_ref, str) and re.fullmatch(r"\d+[a-z]?", extension_ref), extension_ref
    assert isinstance(item, int) and item >= 1, item
    assert isinstance(text, str), type(text)
    result = f"{UNATTRIBUTED_MARKER_PREFIX}ext {extension_ref} step {item}: {text}"
    return result


def unattributed_trigger_marker(text: str) -> str:
    """Build the trigger marker form: ``' UNATTRIBUTED trigger: <text>``."""
    assert isinstance(text, str), type(text)
    result = f"{UNATTRIBUTED_MARKER_PREFIX}trigger: {text}"
    return result


# --- findings ------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """One actionable checker finding (feat-27 convention: line + cause + fix hint).

    Attributes:
        line: 1-based line number in the checked source.
        message: the cause, plain and direct.
        fix_hint: the concrete fix for the author/agent.
    """

    line: int
    message: str
    fix_hint: str


@dataclass(frozen=True)
class StructureCheckResult:
    """The outcome of :func:`check_structure`.

    Attributes:
        ok: ``True`` when :attr:`errors` is empty (warnings never block).
        errors: the blocking findings (mode-dependent for the lenient set).
        warnings: the non-blocking findings (both modes for UNATTRIBUTED
            markers and raw-quote notices; the lenient set in preflight).
    """

    ok: bool
    errors: list[Finding]
    warnings: list[Finding]


# --- line grammar (the emitted subset, rulebook §6.1) ---------------------------

_COMMENT_MARKER = "'"
_AT_STARTUML_PATTERN = re.compile(r"^\s*@startuml\b")
_AT_ENDUML_PATTERN = re.compile(r"^\s*@enduml\b")
_AT_BARE_END_PATTERN = re.compile(r"^\s*@end\s*$")
_END_NOTE_PATTERN = re.compile(r"^\s*end note\b")
_END_NAMED_PATTERN = re.compile(r"^\s*end\s+([A-Za-z]+)\s*$")
_END_BARE_PATTERN = re.compile(r"^\s*end\s*$")
_FRAGMENT_OPEN_PATTERN = re.compile(r"^\s*(alt|opt|loop|group|box|rectangle|package)\b")
#: A note line. A note with a colon on its line is a SINGLE-LINE placement
#: note (``note bottom of uc1: "text"`` — the package edge notes); only a
#: colon-free note line (``note``/``note right``/``note left``/
#: ``note bottom of X``) OPENS a block that must end with ``end note``.
_NOTE_LINE_PATTERN = re.compile(r"^\s*note\b")
_STEREOTYPE_RUN_PATTERN = re.compile(r"^(?:\s*<<[^<>]*>>)+$")
_DECLARATION_PATTERN = re.compile(r"^\s*(actor|participant|usecase)\s+(?P<rest>\S.*)$")
#: Fragments a BARE ``end`` may close (the real parser rejects a bare ``end``
#: on box/package/rectangle and on an empty stack — verified against 1.2026.8).
_BARE_END_CLOSEABLE = ("alt", "opt", "loop", "group")
_OPERAND = r"(?:\"[^\"]*\"|\S+)"
_ARROW_PATTERN = re.compile(
    rf"^\s*(?P<src>{_OPERAND})\s+(?P<arrow>-->|->)\s*(?P<dst>{_OPERAND})?\s*(?::\s*(?P<text>.*))?$"
)
_EDGE_PATTERN = re.compile(rf"^\s*(?P<src>{_OPERAND})\s+\.\.>\s*(?P<dst>{_OPERAND})?\s*(?::\s*(?P<label>.*))?$")
_AS_ALIAS_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*")


def _strip_operand(token: str) -> str:
    """Unwrap a quoted operand and undo the ``#quot;`` sanitisation."""
    if len(token) >= 2 and token.startswith('"') and token.endswith('"'):
        return token[1:-1].replace("#quot;", '"')
    return token


def _declaration_parts(rest: str) -> tuple[str, str | None, str | None, list[Finding]]:
    """Split a declaration's ``rest`` into (label, alias, stereotype_tail).

    Returns the parts plus local findings (unbalanced quote / stereotype).
    The label is the quoted substring's content or the bare run up to
    `` as ``/`` <<``; the alias only from a trailing ``as <ident>``.
    """
    findings: list[Finding] = []
    if rest.startswith('"'):
        close = rest.find('"', 1)
        if close == -1:
            return (
                "",
                None,
                None,
                [
                    Finding(
                        0,
                        "unbalanced double quote in declaration label (the quote never closes on this line)",
                        "close the label's quote, or sanitise an embedded quote as #quot; (rulebook §2.4)",
                    )
                ],
            )
        label = rest[1:close]
        remainder = rest[close + 1 :]
    else:
        parts = re.split(r"\s+as\s+|\s+<<", rest, maxsplit=1)
        label = parts[0].strip()
        remainder = parts[1] if len(parts) > 1 else ""
    keyword_match = re.match(r"^\s*as\s+", remainder)
    if keyword_match is not None:
        remainder = remainder[keyword_match.end() :]
    alias = None
    alias_match = _AS_ALIAS_PATTERN.match(remainder)
    if alias_match is not None:
        alias = alias_match.group(1)
        remainder = remainder[alias_match.end() :]
    tail = remainder.strip()
    if ("<<" in tail or ">>" in tail) and not _STEREOTYPE_RUN_PATTERN.match(tail):
        findings.append(
            Finding(
                0,
                "unbalanced <<stereotype>> in declaration (an opening/closing << is missing)",
                "write the stereotype as <<word>> (both brackets, no nesting)",
            )
        )
    return label, alias, tail, findings


def check_structure(text: str, mode: str = MODE_STANDALONE) -> StructureCheckResult:
    """Lint ``text`` as the emitted PlantUML subset (rulebook §6).

    Parameters
    ----------
    text:
        The full diagram source (one or more ``@startuml`` ... ``@enduml``
        blocks; the packaged shape is a single block).
    mode:
        :data:`MODE_PREFLIGHT` (lenient set = warnings) or
        :data:`MODE_STANDALONE` (lenient set = errors). See the module
        docstring for the contract.

    Returns
    -------
    StructureCheckResult
        ``ok`` plus the ``errors``/``warnings`` findings (1-based line +
        cause + fix hint each). Never raises on diagram content.
    """
    assert isinstance(text, str), type(text)
    assert mode in _MODES, f"mode must be one of {_MODES}, got {mode!r}"

    lines = text.split("\n")
    errors: list[Finding] = []
    warnings: list[Finding] = []
    lenient: list[Finding] = []

    startuml_seen = False
    in_block = False  # inside an @startuml...@enduml block
    in_note = False
    note_open_line = 0
    fragments: list[tuple[str, int]] = []  # (kind, open line)
    # declared operand names (alias + label), for the sequence subset
    declared: set[str] = set()
    undeclared_reported: dict[str, int] = {}  # name -> first line (lenient #5, deduped)

    def error(line: int, message: str, fix_hint: str) -> None:
        errors.append(Finding(line, message, fix_hint))

    def warn(line: int, message: str, fix_hint: str) -> None:
        warnings.append(Finding(line, message, fix_hint))

    def lenient_finding(line: int, message: str, fix_hint: str) -> None:
        lenient.append(Finding(line, message, fix_hint))

    def close_note(line: int, opener: str = "end note") -> None:
        nonlocal in_note
        if not in_note:
            error(
                line,
                f"stray {opener!r} without an open note block",
                "remove the extra 'end note', or add the matching 'note'/'note right' opener",
            )
            return
        in_note = False

    def block_boundary(line: int, enduml_at_line: bool) -> None:
        """Run the at-block-end checks for the current block.

        ``enduml_at_line=True`` (the boundary IS an ``@enduml`` line) skips
        the missing-@enduml lenient finding — that one fires only at a true
        EOF (the parser-verified lenient case is a missing ``@enduml``).
        """
        nonlocal in_block, in_note, note_open_line
        if in_note:
            error(
                note_open_line,
                "note block opened here is never closed before the diagram ends",
                "close the note with an 'end note' line (the real parser rejects an unclosed note)",
            )
            in_note = False
        while fragments:
            kind, open_line = fragments.pop()
            lenient_finding(
                open_line,
                f"unclosed {kind!r} fragment at the end of the diagram (the parser closes it implicitly)",
                "add a matching 'end' line (the real parser accepts the omission)",
            )
        if in_block and not enduml_at_line:
            lenient_finding(
                line,
                "missing @enduml (the parser ends the diagram at EOF)",
                "add an @enduml line at the end of the diagram (the real parser accepts its absence)",
            )
        in_block = False

    for number, raw_line in enumerate(lines, start=1):
        line = raw_line
        stripped = line.strip()

        if not stripped:
            continue

        # --- comment lines (and UNATTRIBUTED markers) ---
        if stripped.startswith(_COMMENT_MARKER):
            if is_unattributed_marker(stripped):
                warn(
                    number,
                    "UNATTRIBUTED marker: this message has no deterministic attribution yet",
                    "replace the marker with an attributed '{sender} -> {receiver}: {text}' arrow "
                    "(rulebook §2.9.3) — the zero-marker rule is enforced by the agent flow, not the checker",
                )
            continue

        # --- block markers ---
        if _AT_STARTUML_PATTERN.match(line):
            if in_block:
                # the parser accepts multiple diagrams in one file (verified
                # against 1.2026.8) — close the previous block leniently
                block_boundary(number, enduml_at_line=False)
            startuml_seen = True
            in_block = True
            continue
        if _AT_ENDUML_PATTERN.match(line):
            # a stray @enduml (no open block) is silently ignored — the real
            # parser is authoritative, and the missing-@startuml finding at
            # EOF already covers the no-diagram case
            if in_block:
                block_boundary(number, enduml_at_line=True)
            continue
        if not in_block and not startuml_seen:
            # content before any @startuml — not the emitted subset; the
            # missing-@startuml finding is reported at EOF instead
            continue

        # --- the lenient bare @end (rulebook §6.4 case 3) ---
        if _AT_BARE_END_PATTERN.match(line):
            if fragments:
                kind, open_line = fragments.pop()
                lenient_finding(
                    number,
                    f"bare @end closes the {kind!r} fragment opened at line {open_line} by name omission "
                    "(the parser accepts it)",
                    "write the named close ('end' or 'end {kind}') instead (the real parser accepts the bare @end)",
                )
            # a bare @end with an empty fragment stack is also parser-accepted
            # (verified against 1.2026.8) — no finding
            continue

        # --- note blocks ---
        if in_note:
            if _END_NOTE_PATTERN.match(line):
                close_note(number)
                continue
            if _END_BARE_PATTERN.match(line) or _END_NAMED_PATTERN.match(line) or _AT_BARE_END_PATTERN.match(line):
                error(
                    number,
                    "an 'end' line inside a note block does not close it (only 'end note' does)",
                    "replace the 'end' with 'end note' (the real parser rejects a bare end here)",
                )
                continue
            # note content line (2-space indented or bare, including lines that
            # start with 'note') — verbatim, no check
            continue
        if _NOTE_LINE_PATTERN.match(line):
            if ":" in line:
                # a single-line placement note (e.g. 'note bottom of uc1: "text"'
                # — the package edge notes) — no block state
                continue
            in_note = True
            note_open_line = number
            continue

        # --- fragment stack ---
        fragment_open = _FRAGMENT_OPEN_PATTERN.match(line)
        if fragment_open is not None:
            fragments.append((fragment_open.group(1), number))
            continue
        if _END_NOTE_PATTERN.match(line):
            # a stray 'end note' outside a note block (the parser rejects it)
            close_note(number)
            continue
        if _END_NAMED_PATTERN.match(line) is not None or _END_BARE_PATTERN.match(line) is not None:
            named_match = _END_NAMED_PATTERN.match(line)
            if not fragments:
                error(
                    number,
                    f"stray {'end ' + named_match.group(1) if named_match else 'end'} with no open fragment",
                    "remove the extra 'end', or add the matching 'alt'/'opt'/... opener",
                )
                continue
            top_kind, open_line = fragments[-1]
            if named_match is None:
                # bare 'end'
                if top_kind not in _BARE_END_CLOSEABLE:
                    error(
                        open_line,
                        f"bare 'end' at line {number} cannot close the {top_kind!r} fragment "
                        "opened at line "
                        f"{open_line} (the parser requires a named end or @end)",
                        f"close it with 'end {top_kind}' (or the lenient bare @end)",
                    )
                else:
                    fragments.pop()
            else:
                if named_match.group(1).lower() != top_kind:
                    warn(
                        number,
                        f"'end {named_match.group(1)}' does not name the innermost open fragment "
                        f"{top_kind!r} (opened at line {open_line}); the parser tolerates the mismatch",
                        f"rename the close to 'end {top_kind}', or reorder the fragments",
                    )
                fragments.pop()
            continue

        # --- declarations ---
        declaration = _DECLARATION_PATTERN.match(line)
        if declaration is not None:
            kind = declaration.group(1)
            label, alias, _remainder, decl_findings = _declaration_parts(declaration.group("rest"))
            for finding in decl_findings:
                error(number, finding.message, finding.fix_hint)
            names = {name for name in (label, alias) if name}
            declared.update(names)
            if kind in ("actor", "participant"):
                # nothing else — sequence operand pool
                pass
            continue

        # --- sequence messages (-> and --> with a colon) and associations ---
        arrow_match = _ARROW_PATTERN.match(line)
        if arrow_match is not None:
            source = _strip_operand(arrow_match.group("src"))
            destination_token = arrow_match.group("dst")
            destination = _strip_operand(destination_token) if destination_token else ""
            message_text = arrow_match.group("text")
            if not destination and message_text is None:
                # dangling arrow (rulebook §6.4 case 4): no target on the line
                # (the parser accepts both 'A -->' and 'A ->' — verified)
                lenient_finding(
                    number,
                    f"dangling arrow {source!r} {arrow_match.group('arrow')} with no target on the line "
                    "(the parser tolerates it)",
                    "complete the arrow with a target participant (the real parser accepts the dangling form)",
                )
                continue
            if not destination and message_text is not None:
                # 'A --> : text' — parser-accepted (verified); not one of the
                # five lenient cases, so no finding
                continue
            if message_text is not None:
                # a sequence message: undeclared operands (rulebook §6.4 case 5)
                for operand in (source, destination):
                    if operand and operand not in declared and operand not in undeclared_reported:
                        undeclared_reported[operand] = number
                        lenient_finding(
                            number,
                            f"undeclared participant {operand!r} in a sequence message (the parser auto-creates it)",
                            "add an 'actor'/'participant' declaration for this name (the real parser "
                            "accepts the omission)",
                        )
                if '"' in message_text:
                    warn(
                        number,
                        "raw double quote in the message text",
                        "sanitise embedded quotes as #quot; (rulebook §2.4)",
                    )
            else:
                # a usecase association (no colon): operands auto-created by the
                # parser too — a notice, not one of the five lenient cases
                for operand in (source, destination):
                    if operand and operand not in declared and operand not in undeclared_reported:
                        undeclared_reported[operand] = number
                        warn(
                            number,
                            f"undeclared node {operand!r} in an association (the parser auto-creates it)",
                            "add an 'actor'/'usecase' declaration for this name",
                        )
            continue

        # --- package edges (..>) ---
        edge_match = _EDGE_PATTERN.match(line)
        if edge_match is not None:
            source = _strip_operand(edge_match.group("src"))
            destination = edge_match.group("dst")
            destination = _strip_operand(destination) if destination and destination.strip() else ""
            for operand in (source, destination):
                if operand and operand not in declared and operand not in undeclared_reported:
                    undeclared_reported[operand] = number
                    warn(
                        number,
                        f"undeclared node {operand!r} in a package edge (the parser auto-creates it)",
                        "add a 'usecase' declaration for this name",
                    )
            label = edge_match.group("label")
            if label is not None and '"' in label:
                warn(
                    number,
                    "raw double quote in the edge label",
                    "sanitise embedded quotes as #quot; (rulebook §2.4)",
                )
            continue

        # anything else (skinparam, title, other diagram content) is accepted
        # silently — the real parser is authoritative outside the subset

    # --- EOF: the missing-@startuml error (both modes) + the last block's tail ---
    if not startuml_seen:
        error(
            1,
            "no @startuml line found (the diagram has no start marker)",
            "add an '@startuml {title}' line as the first line — a payload without @startuml is "
            "nothing-extractable to the server and exit 1 to 'specmgr plantuml-check'",
        )
    else:
        block_boundary(len(lines), enduml_at_line=False)

    # --- mode promotion of the lenient set ---
    if mode == MODE_STANDALONE:
        errors.extend(lenient)
    else:
        warnings.extend(lenient)

    result = StructureCheckResult(ok=not errors, errors=errors, warnings=warnings)
    return result
