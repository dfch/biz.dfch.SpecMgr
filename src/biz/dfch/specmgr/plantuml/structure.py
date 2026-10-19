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
sequence files): ``@startuml``/``@enduml`` presence,
actor/participant/usecase/component declarations (quoted or bare labels,
``as`` aliases — a bare identifier or, since the 2026-10-10 amendment, a
bracketed ``[...]`` token recorded unbracketed — ``<<stereotypes>>``),
usecase associations (``-->``), package edges (``..>``), sequence messages
(``->``/``-->``/self), note blocks, the fragment stack (``alt``/``opt``/
``loop``/``group``/``box``/``rectangle``/``package`` with ``end``), quote
sanitisation (the ``#quot;`` convention), and ``'`` comment lines — including
UNATTRIBUTED-marker detection.

Each ``@startuml``…``@enduml`` block is an **independent linting unit**
(the 2026-10-08 amendment): the block-scoped state — the declaration table,
the undeclared-name dedup table, the fragment stack, and the note state —
resets at every block boundary (an ``@enduml``, a stray ``@enduml``, or the
next ``@startuml`` closing a block that is missing its ``@enduml``). A
lenient finding (e.g. an unclosed fragment) is attributed within the block it
belongs to, and lines outside any block (before the first ``@startuml``, or
between two blocks) carry no findings. The parser is authoritative for
multi-block files — it accepts them (verified against 1.2026.8, including
the missing-``@enduml``-then-next-``@startuml`` shape); the packaged shape
is a single block.

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
``@startuml`` is an error in **both** modes (the emitted subset always
starts with ``@startuml`` — the normative rule is the emitted-subset
contract, not the server's own behaviour for such payloads, which drifts
between builds: rulebook §5.2 drift note (a), re-probed 2026-10-06).
UNATTRIBUTED markers are warnings in both
modes (deliberate placeholders — syntactically ``'`` comments the real parser
accepts; the zero-marker rule is enforced by the agent flow, not here).

The 2026-10-15 tripwire amendment (feat-214-rel-invalid-diag, the reference-
graph rulebook §7.1): the ``never rejects what the parser accepts`` invariant
forbids false positives, not false negatives — and the demonstrated gap was a
false negative (the pre-amendment checker reported zero findings in both
modes over the parser-rejected braceless ``package "TYPE" … end package``
grouping of component declarations). The amendment is the reverse direction:
a ``package`` fragment that COLLECTS component declarations (a ``component``
keyword declaration line or a short-form ``[X]`` line) must close with a
``}`` line — a named ``end package`` close (after a braceless-open or a
curly-open) and an unclosed such fragment at a block boundary are errors in
BOTH modes, with a fix hint naming the curly-brace group form
(``component "TYPE" { … }``). The rule is content-conditional: ``package``
fragments holding sequence content (participants — the UC subset,
parser-verified in feat-185) collect no component declaration and stay
exactly as before.

The 2026-10-17 fix (feat-214-rel-invalid-diag Phase 140, E1) corrects a
false positive the pre-fix implementation introduced against its own rule:
a ``}`` line was silently skipped by the line grammar and never popped the
fragment stack, so a curly-opened ``package "X" {`` fragment that collected
a component declaration and was closed with the rule's OWN required close
(a ``}`` line — real-parser-accepted, verified against the pinned 1.2026.8)
was reported at the block boundary as "never closed with '}'" — an error in
BOTH modes and a factually wrong diagnosis (the close was present). A
``}`` line now closes (pops) the innermost curly-open fragment, with no
finding on the pop itself; the tripwire fires only on a named ``end
package`` close over a component-collecting fragment and on such a fragment
still open at a block boundary (where the diagnostic's "never closed"
wording is factually correct again). A ``}`` with no curly-open fragment
open (the curly ``component "TYPE" { … }`` domain groups and the ``skinparam
component { … }`` block — declarations/skinparam, not fragments) stays
silently accepted, exactly as before.

The 2026-10-18 fix (feat-214-rel-invalid-diag Phase 150, E1/E2/I1) corrects
the two tripwire firing sites the 2026-10-15 amendment froze WITHOUT a
parser verdict (the 2026-10-15 isolation matrix verified only the NAMED-
CLOSE shapes): a component-collecting ``package`` fragment UNCLOSED AT THE
BLOCK BOUNDARY (every open shape) and one closed by a BARE ``@end`` (every
open shape) are parser-ACCEPTED by the pinned 1.2026.8 (file- and
pipe-form, recorded in the feature plan's More Information matrix). The
block-boundary site is therefore a LENIENT finding — mirroring the generic
else branch: a warning in preflight, promoted to an error in standalone, a
content-conditional variant of the "unclosed fragment at EOF" lenient case;
the 2026-10-15 comment's claim that "the parser does not implicitly close
such a block into a valid diagram" was empirically false for these shapes.
The bare-``@end`` site emits the tripwire's own lenient finding (a
content-conditional variant of the "bare ``@end``" lenient case) instead of
the generic name-omission finding — whose hint would steer the author to
the parser-rejected named close. The NAMED-CLOSE site (an ``end package``
over a component declaration, both open shapes) STAYS an error in BOTH
modes — parser-rejected, re-verified 2026-10-18. The fix hint is split by
the CLOSE KIND (the firing site; axis corrected in Phase 160 — the
2026-10-18 open-shape split proved precise for only 2 of the 6 site ×
open-shape combinations, because the remedy depends on which close line
exists, not how the block opened; the open shape stays named in all three
sites' messages): named close — replace the ``end package`` close with a
``}`` line; unclosed at boundary — add the missing ``}`` line; bare
``@end`` close — replace the bare ``@end`` close with a ``}`` line; each
variant keeps the common tail "or convert the group to the ``component
"TYPE" { … }`` domain-group form" — the 2026-10-15 single hint's "an
unclosed block over component declarations is a parser syntax error"
clause was factually false for the accepted shapes.

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


def is_unattributed_marker(line: str) -> bool:
    """Return ``True`` if ``line`` is an UNATTRIBUTED marker comment line.

    Detection is by the shared :data:`UNATTRIBUTED_MARKER_PREFIX` on a
    comment line only — deliberately prefix-only, no tail-grammar
    validation: a marker line is a comment and its tail is free text the
    agent will replace, so strictness here would create false negatives for
    nothing.
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


@dataclass
class _FragmentState:
    """One open fragment on the checker's line-oriented stack (internal state).

    The 2026-10-15 tripwire amendment extends the pre-amendment
    ``(kind, open line)`` tuple with two recorded facts: :attr:`curly_open`
    (the open line ends with ``{``) and :attr:`has_component` (the fragment
    collected a component declaration — a ``component`` keyword line or a
    short-form ``[X]`` line — since the open). Only ``package`` fragments are
    subject to the tripwire; the fields are recorded for every fragment kind.

    Attributes:
        kind: the fragment keyword (``alt``/``opt``/``loop``/``group``/
            ``box``/``rectangle``/``package``).
        open_line: the 1-based line of the fragment open.
        curly_open: ``True`` when the open line ends with ``{``.
        has_component: ``True`` once the fragment collected a component
            declaration (the tripwire's content condition).
    """

    kind: str
    open_line: int
    curly_open: bool = False
    has_component: bool = False


# --- line grammar (the emitted subset, rulebook §6.1) ---------------------------

_COMMENT_MARKER = "'"
_AT_STARTUML_PATTERN = re.compile(r"^\s*@startuml\b")
_AT_ENDUML_PATTERN = re.compile(r"^\s*@enduml\b")
_AT_BARE_END_PATTERN = re.compile(r"^\s*@end\s*$")
_END_NOTE_PATTERN = re.compile(r"^\s*end note\b")
_END_NAMED_PATTERN = re.compile(r"^\s*end\s+([A-Za-z]+)\s*$")
_END_BARE_PATTERN = re.compile(r"^\s*end\s*$")
_FRAGMENT_OPEN_PATTERN = re.compile(r"^\s*(alt|opt|loop|group|box|rectangle|package)\b")
#: The short-form component line (the 2026-10-15 tripwire amendment): a line
#: consisting of EXACTLY ONE bracketed token (the frozen alias shape — no
#: whitespace, no brackets inside) and nothing else. The real parser reads it
#: as a component declaration (the Q1 isolation matrix of the reference-graph
#: rulebook §4.3), so for the tripwire it counts as a component declaration
#: the enclosing package fragment collects.
_SHORT_COMPONENT_LINE = re.compile(r"^\s*(\[[^\[\]\s]+\])\s*$")


def _package_component_fix(close_kind: str) -> str:
    """The tripwire fix hint, keyed by the close kind — the firing site (2026-10-18, I1; axis corrected in Phase 160).

    The 2026-10-15 single hint conflated the remedies and was
    factually false for the parser-accepted unclosed shapes (its "an
    unclosed block over component declarations is a parser syntax error"
    clause — the pinned 1.2026.8 accepts every unclosed-at-boundary
    variant and the bare-``@end`` close, file- and pipe-form; the
    reference-graph rulebook §7.1 Phase 150 note). The Phase 150 split
    keyed the remedy on the recorded OPEN SHAPE — precise for only 2 of
    the 6 site × open-shape combinations (a braceless open at the
    named-close site has nothing missing to add: its block IS closed, by
    the parser-rejected ``end package`` line; a curly open at the
    block-boundary site has no ``end package`` line to replace). The
    remedy depends on which CLOSE LINE exists at the firing site, so the
    axis is the close kind (the open shape stays named in all three
    sites' messages — no information lost):

    - ``named-close`` — the ``end package`` close is parser-rejected:
      REPLACE it with a ``}`` line (→ one of the parser-verified
      ACCEPTED ``}``-close shapes, re-probed Phase 160, both open
      shapes, pipe-form rc=0).
    - ``block-boundary`` — no close line exists (the parser closes the
      block implicitly): ADD the missing ``}`` line (→ the same
      verified shapes).
    - ``bare-@end`` — the bare ``@end`` close is parser-accepted but
      names no fragment: REPLACE it with a ``}`` line (→ the same
      verified shapes).

    ``close_kind`` is the firing site's own vocabulary (``"named-close"``
    / ``"block-boundary"`` / ``"bare-@end"`` — the same strings the call
    sites pass); every variant keeps the common tail naming the
    curly-brace domain-group form the real parser accepts for a
    component-diagram group holding component declarations.
    """
    assert close_kind in ("named-close", "block-boundary", "bare-@end"), close_kind
    if close_kind == "named-close":
        primary = "replace the 'end package' close with a '}' line"
    elif close_kind == "block-boundary":
        primary = "add the missing '}' line"
    else:
        primary = "replace the bare '@end' close with a '}' line"
    result = f"{primary} (or convert the group to the curly-brace domain-group form 'component \"TYPE\" {{ … }}')"
    return result


#: A note line. A note with a colon on its line is a SINGLE-LINE placement
#: note (``note bottom of uc1: "text"`` — the package edge notes); only a
#: colon-free note line (``note``/``note right``/``note left``/
#: ``note left of X``/``note right of X``/``note bottom of X`` — the anchored
#: forms the renderers emit for unanchored sequence notes since the 2026-10-06
#: amendment) OPENS a block that must end with ``end note``.
_NOTE_LINE_PATTERN = re.compile(r"^\s*note\b")
_STEREOTYPE_RUN_PATTERN = re.compile(r"^(?:\s*<<[^<>]*>>)+$")
#: The declaration keywords (rulebook §6.1, amended 2026-10-10 — the
#: reference-graph emission's ``component`` nodes join the UC subset's
#: actor/participant/usecase).
_DECLARATION_PATTERN = re.compile(r"^\s*(actor|participant|usecase|component)\s+(?P<rest>\S.*)$")
#: Fragments a BARE ``end`` may close (the real parser rejects a bare ``end``
#: on box/package/rectangle and on an empty stack — verified against 1.2026.8).
_BARE_END_CLOSEABLE = ("alt", "opt", "loop", "group")
_OPERAND = r"(?:\"[^\"]*\"|\S+)"
_ARROW_PATTERN = re.compile(
    rf"^\s*(?P<src>{_OPERAND})\s+(?P<arrow>-->|->)\s*(?P<dst>{_OPERAND})?\s*(?::\s*(?P<text>.*))?$"
)
_EDGE_PATTERN = re.compile(rf"^\s*(?P<src>{_OPERAND})\s+\.\.>\s*(?P<dst>{_OPERAND})?\s*(?::\s*(?P<label>.*))?$")
#: The frozen alias token (rulebook §6.1, amended 2026-10-10): a bare
#: identifier, or a bracketed ``[...]`` token with no whitespace and no
#: brackets inside (the reference-graph alias shape) — the declared name is
#: recorded UNBRACKETED (via :func:`_strip_operand`'s own bracket unwrap).
_ALIAS_TOKEN = r"(?:[A-Za-z_][A-Za-z0-9_]*|\[[^\[\]\s]+\])"
_AS_ALIAS_PATTERN = re.compile(rf"^\s*({_ALIAS_TOKEN})\s*")


def _strip_operand(token: str) -> str:
    """Unwrap a quoted or fully-bracketed operand and undo the ``#quot;`` sanitisation.

    The bracket unwrap (the 2026-10-10 amendment, rulebook §6.1) makes a
    bracketed edge operand (e.g. ``[REQ-{uuid}]``) compare identically to the
    unbracketed name a declaration's bracketed ``as`` alias records.
    """
    if len(token) >= 2 and token.startswith('"') and token.endswith('"'):
        return token[1:-1].replace("#quot;", '"')
    if len(token) >= 2 and token.startswith("[") and token.endswith("]"):
        return token[1:-1]
    return token


#: A balanced stereotype run — one or more ``<<…>>`` pairs (whitespace
#: allowed inside the brackets, no nesting) with its leading whitespace.
#: The frozen declaration shape's tail (rulebook §6.1): a quoted or bare
#: label, an optional ``as <ident>`` alias, and an optional trailing run —
#: the run is the stereotype **with or without the alias** (the 2026-10-08
#: amendment — the pre-amendment split consumed a `` <<`` separator and
#: misread the stereotype's inside as the alias, false-rejecting
#: ``participant Alice <<user>>`` in both modes).
_STEREOTYPE_RUN = r"(?:\s*<<[^<>]*>>)+"

#: The frozen declaration shapes (rulebook §6.1, amended 2026-10-08 and
#: 2026-10-10 — the bracketed ``as`` alias) — the bare form (label = one
#: token; a multi-word bare label is not the emitted subset) and the quoted
#: form's remainder after the closing quote.
_BARE_DECLARATION_SHAPE = re.compile(rf"^(\S+)(?:\s+as\s+({_ALIAS_TOKEN}))?({_STEREOTYPE_RUN})?\s*$")
_QUOTED_DECLARATION_SHAPE = re.compile(rf"^\s*(?:as\s+({_ALIAS_TOKEN}))?({_STEREOTYPE_RUN})?\s*$")


def _declaration_parts(rest: str) -> tuple[str, str | None, str | None, list[Finding]]:
    """Split a declaration's ``rest`` into (label, alias, stereotype_tail).

    Returns the parts plus local findings (unbalanced quote / stereotype).
    The label is the quoted substring's content or the bare token; the alias
    only from an ``as <alias>`` (a bare identifier or, since the 2026-10-10
    amendment, a bracketed ``[...]`` token — recorded unbracketed); a
    trailing balanced ``<<…>>`` run is the stereotype tail — with or without
    the alias in between (the 2026-10-08 amendment). A bracket shape that is
    NOT the frozen one is an unbalanced ``<<stereotype>>`` error (the
    negative control ``participant A <<user`` — the real parser answers it
    400 — errors in both modes).
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
        shape = _QUOTED_DECLARATION_SHAPE.match(remainder)
        if shape is not None:
            tail = (shape.group(2) or "").strip()
            alias = shape.group(1)
            if alias is not None:
                alias = _strip_operand(alias)  # 2026-10-10: a bracketed alias records unbracketed
            return label, alias, tail, findings
    else:
        shape = _BARE_DECLARATION_SHAPE.match(rest)
        if shape is not None:
            tail = (shape.group(3) or "").strip()
            alias = shape.group(2)
            if alias is not None:
                alias = _strip_operand(alias)  # 2026-10-10: a bracketed alias records unbracketed
            return shape.group(1), alias, tail, findings
        if "<<" in rest or ">>" in rest:
            # a bracket shape outside the frozen form: the legacy walk
            # below derives label/alias as before, and the unbalanced
            # finding is added when the legacy walk did not already flag
            # the tail ('participant A <<user' swallows the ' <<' separator
            # into the alias, so the legacy tail check alone misses it)
            label, alias, tail, findings = _declaration_parts_legacy(rest)
            if not findings:
                findings.append(
                    Finding(
                        0,
                        "unbalanced <<stereotype>> in declaration (an opening/closing << is missing)",
                        "write the stereotype as <<word>> (both brackets, no nesting)",
                    )
                )
            return label, alias, tail, findings
    return _declaration_parts_legacy(rest)


def _declaration_parts_legacy(rest: str) -> tuple[str, str | None, str | None, list[Finding]]:
    """The pre-2026-10-08 ``_declaration_parts`` walk, kept for the shapes the
    frozen-form regexes above do not cover (byte-identical behavior for
    every shape the legacy path handles)."""
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
        alias = _strip_operand(alias_match.group(1))  # 2026-10-10: a bracketed alias records unbracketed
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


def _mark_component_fragment(fragments: list[_FragmentState]) -> None:
    """Record a component declaration on the innermost open ``package`` fragment (internal state).

    The 2026-10-15 tripwire's content condition: a component declaration
    (a ``component`` keyword line or a short-form ``[X]`` line) marks the
    nearest enclosing ``package`` fragment as component-collecting. A
    declaration outside any ``package`` fragment (top-level, or inside a
    non-package fragment) is a no-op — the tripwire is scoped to ``package``
    fragments only (the reference-graph rulebook §7.1).
    """
    for fragment in reversed(fragments):
        if fragment.kind == "package":
            fragment.has_component = True
            return


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
    fragments: list[_FragmentState] = []  # (kind, open line, curly open, component collected)
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
            fragment = fragments.pop()
            if fragment.kind == "package" and fragment.has_component:
                # the 2026-10-15 tripwire, 2026-10-18 demotion (feat-214-
                # rel-invalid-diag Phase 150, E1): the unclosed-at-boundary
                # shape is parser-ACCEPTED (pinned 1.2026.8, file- and
                # pipe-form, every open shape — rulebook §7.1 Phase 150
                # note), so the site is a lenient finding mirroring the
                # else branch: a content-conditional variant of the
                # "unclosed fragment at EOF" lenient case (warning in
                # preflight, promoted error in standalone). The 2026-10-15
                # comment's claim ("the parser does not implicitly close
                # such a block into a valid diagram") was verified only for
                # the NAMED-CLOSE shapes and is empirically false here; the
                # named-close site stays an error in BOTH modes.
                open_shape = "curly-open" if fragment.curly_open else "braceless"
                lenient_finding(
                    fragment.open_line,
                    f"package fragment that collects component declarations (opened at line "
                    f"{fragment.open_line}, {open_shape}) is unclosed at the block boundary "
                    "(the parser accepts the omission and closes the block implicitly)",
                    _package_component_fix("block-boundary"),
                )
            else:
                lenient_finding(
                    fragment.open_line,
                    f"unclosed {fragment.kind!r} fragment at the end of the diagram (the parser closes it implicitly)",
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

        # --- note content: the in_note state takes precedence over every
        # block-marker detection below (rulebook §6.3 — the checker never
        # rejects what the parser accepts; a note-content line that starts
        # with @startuml / @enduml / @end, or that is exactly ``end``, is
        # content — verified rendered by both sources 2026-10-06) ---
        if in_note:
            if _END_NOTE_PATTERN.match(line):
                close_note(number)
            # note content line (2-space indented or bare, including lines
            # that start with 'note' or 'end') — verbatim, no check
            continue

        # --- block markers (each @startuml...@enduml block is an independent
        # linting unit — the 2026-10-08 amendment: on every boundary the
        # fragment stack closes out the way EOF does, then the block-scoped
        # state resets, so findings never leak across blocks) ---
        if _AT_STARTUML_PATTERN.match(line):
            if in_block:
                # the parser accepts multiple diagrams in one file (verified
                # against 1.2026.8, including a missing @enduml answered by
                # the next @startuml) — close the previous block leniently,
                # then start fresh
                block_boundary(number, enduml_at_line=False)
                declared = set()
                undeclared_reported = {}
            startuml_seen = True
            in_block = True
            continue
        if _AT_ENDUML_PATTERN.match(line):
            # a stray @enduml (no open block) is silently ignored — the real
            # parser is authoritative (verified: it answers 200 for a stray
            # @enduml), and the missing-@startuml finding at EOF already
            # covers the no-diagram case
            if in_block:
                block_boundary(number, enduml_at_line=True)
                declared = set()
                undeclared_reported = {}
            continue
        if not in_block:
            # content outside any @startuml...@enduml block (before the first
            # diagram, or between two) — not part of any linting unit; the
            # missing-@startuml finding is reported at EOF instead
            continue

        # --- the lenient bare @end (rulebook §6.4 case 3) ---
        if _AT_BARE_END_PATTERN.match(line):
            if fragments:
                fragment = fragments.pop()
                if fragment.kind == "package" and fragment.has_component:
                    # the 2026-10-18 fix (feat-214-rel-invalid-diag Phase
                    # 150, E2): a component-collecting package closed by a
                    # bare @end is parser-ACCEPTED (pinned 1.2026.8, file-
                    # and pipe-form, every open shape) — the tripwire's own
                    # lenient finding (aligned with the block-boundary
                    # treatment) instead of the generic name-omission
                    # finding, whose hint would steer the author to the
                    # NAMED 'end package' close — exactly the parser-
                    # rejected shape the named-close error site fires on
                    # (rulebook §7.1 Phase 150 note).
                    open_shape = "curly-open" if fragment.curly_open else "braceless"
                    lenient_finding(
                        number,
                        f"bare @end closes the package fragment that collects component "
                        f"declarations (opened at line {fragment.open_line}, {open_shape}) by "
                        "name omission (the parser accepts it)",
                        _package_component_fix("bare-@end"),
                    )
                else:
                    lenient_finding(
                        number,
                        f"bare @end closes the {fragment.kind!r} fragment opened at line "
                        f"{fragment.open_line} by name omission (the parser accepts it)",
                        "write the named close ('end' or 'end {kind}') instead (the real parser accepts the bare @end)",
                    )
            # a bare @end with an empty fragment stack is also parser-accepted
            # (verified against 1.2026.8) — no finding
            continue

        # --- note block openers ---
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
            fragments.append(
                _FragmentState(
                    kind=fragment_open.group(1),
                    open_line=number,
                    curly_open=stripped.endswith("{"),
                )
            )
            continue
        if stripped == "}":
            # a '}' line CLOSES the innermost curly-open fragment (the
            # 2026-10-17 fix, feat-214-rel-invalid-diag Phase 140, E1): the
            # real parser accepts a curly-opened 'package "X" { … }' closed
            # with '}' over component declarations (verified against the
            # pinned 1.2026.8 — the plan's isolation matrix), so the pop is
            # a LEGAL close: no finding is emitted for it, and the fragment
            # no longer reaches the block-boundary tripwire. The scan skips
            # braceless-open fragments (a '}' does not close them), which is
            # what makes nesting pop innermost-first. A '}' with no
            # curly-open fragment open (the curly 'component "TYPE" { … }'
            # domain groups and the 'skinparam component { … }' block —
            # declarations/skinparam, not fragments) is silently accepted,
            # exactly as before.
            for index in range(len(fragments) - 1, -1, -1):
                if fragments[index].curly_open:
                    del fragments[index]
                    break
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
            top = fragments[-1]
            if named_match is None:
                # bare 'end'
                if top.kind not in _BARE_END_CLOSEABLE:
                    error(
                        top.open_line,
                        f"bare 'end' at line {number} cannot close the {top.kind!r} fragment "
                        "opened at line "
                        f"{top.open_line} (the parser requires a named end or @end)",
                        f"close it with 'end {top.kind}' (or the lenient bare @end)",
                    )
                else:
                    fragments.pop()
            else:
                if named_match.group(1).lower() != top.kind:
                    warn(
                        number,
                        f"'end {named_match.group(1)}' does not name the innermost open fragment "
                        f"{top.kind!r} (opened at line {top.open_line}); the parser tolerates the mismatch",
                        f"rename the close to 'end {top.kind}', or reorder the fragments",
                    )
                elif top.kind == "package" and top.has_component:
                    # the 2026-10-15 tripwire (verified parser-failing shapes —
                    # both the braceless-open + 'end package' close and the
                    # curly-open + 'end package' close; re-verified against the
                    # pinned 1.2026.8 in Phase 150, file- and pipe-form): an
                    # error in BOTH modes, reported on the close line (the
                    # recorded open shape is named — the parser rejects both
                    # opens the same way)
                    open_shape = "curly-open" if top.curly_open else "braceless"
                    error(
                        number,
                        f"named 'end package' close of a package fragment that collects component "
                        f"declarations (opened at line {top.open_line}, {open_shape}) — the real "
                        "PlantUML parser rejects component declarations in a package block closed "
                        "with 'end package'",
                        _package_component_fix("named-close"),
                    )
                fragments.pop()
            continue

        # --- short-form component line (the 2026-10-15 tripwire amendment): a
        # line of exactly one bracketed token is a component declaration to the
        # real parser — record the name unbracketed (the alias convention) and
        # mark the enclosing package fragment as component-collecting ---
        short_component = _SHORT_COMPONENT_LINE.match(line)
        if short_component is not None:
            declared.add(_strip_operand(short_component.group(1)))
            _mark_component_fragment(fragments)
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
            if kind == "component":
                # the 2026-10-15 tripwire's content condition
                _mark_component_fragment(fragments)
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
            "add an '@startuml {title}' line as the first line — the emitted subset always starts "
            "with @startuml (rulebook §6.1), and 'specmgr plantuml-check' exits 1 on its absence",
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
