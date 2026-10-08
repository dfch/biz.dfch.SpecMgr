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

"""Deterministic UC → PlantUML renderers (feat-185-uc-diagrams, Phase 110).

Ports the v1-era ``render_uc_diagram`` (Task 2.1 — the v2 package docstring's
"not yet ported" gap) onto ``uc/models/v2``, and adds the two renderers the
frozen rulebook (``specmgr://uc/plantuml``, ``uc/data/uc_plantuml.md`` §2)
specifies: the multi-UC package diagram and the sequence-diagram skeleton.

Three pure functions, all deterministic over their parsed-model inputs — no
file I/O, no network, no clock:

- :func:`render_uc_diagram` (rulebook §2.5–§2.6) — one ``usecase`` node
  (title + level stereotype), one ``actor`` node per distinct cleaned actor
  label, plain ``-->`` associations. Byte-for-byte the rulebook §2.6
  reference rendering for the packaged example (the frozen golden).
- :func:`render_use_case_package` (rulebook §2.7–§2.8) — one node per
  package document, the deduplicated actor union, and the
  ``<<include>>``/``<<extend>>``/superordinate edges from ``Related Use
  Cases``. Takes **resolved facts**, not directory handles: the caller (the
  Phase 120 tool / the Phase 130 CLI) does the disk resolution via
  ``general.tools._doc_paths`` / the uc read path and passes one
  :class:`PackageDocument` per slot — a reference is "in the package" iff its
  uuid is the id of a parsed slot, and everything else takes the deterministic
  unresolvable-note path (the render never fails on a reference).
- :func:`render_uc_sequence_skeleton` (rulebook §2.9) — participants, the
  preconditions note, the trigger (virtual step 0, receiver fixed to the
  system), the steps in 1-based ordinal order with the §2.9.2
  ``str(item)`` decomposition pipeline (marker strip → lead paragraph →
  dedented continuation), §2.9.3 attribution (longest word-boundary
  case-insensitive prefix sender; first sender-distinct text-position
  receiver, else the system; self-message when the sender is the system),
  §2.9.4 UNATTRIBUTED markers (built from the shared
  :mod:`biz.dfch.specmgr.plantuml.structure` constants — never re-stringed),
   §2.9.6 notes (top/final and no-message-to-attach notes anchored as
   ``note left of {primary-actor-alias}``, message-attached ``note right`` —
   amended 2026-10-05, the real 1.2026.8 parser rejects bare ``note``;
   amended 2026-10-06, a bare note after a self-message's note tile crashes
   1.2026.8, so the unanchored notes are anchored on the primary actor's
   alias), §2.9.7 extension
  ``alt`` fragments (anchored at the structurally validated step, single
  condition branch, no ``else``, sibling order, resumption notes for
  Return/Continue-to-step items — standalone or embedded, case-insensitive),
  and sub-variation notes.

Import direction: ``uc`` → ``plantuml`` (the shared marker constant only) —
never the reverse (ADR 7a626b12).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from biz.dfch.specmgr.plantuml.structure import (
    unattributed_ext_marker,
    unattributed_step_marker,
    unattributed_trigger_marker,
)

from .use_case import Extension, SubVariation, UseCase

__all__ = [
    "PackageDocument",
    "render_uc_diagram",
    "render_uc_sequence_skeleton",
    "render_use_case_package",
]

# --- shared, rulebook-frozen helpers ------------------------------------------

#: A PlantUML alias must be a bare identifier (v1's ``_BARE_ALIAS_PATTERN``,
#: ``uc/models/v1/uc_diagram.py`` — the frozen reference; the parity is pinned
#: by the test suite).
_BARE_ALIAS_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

#: The first double-quoted substring in actor text, if any (v1's
#: ``_QUOTED_SUBSTRING_PATTERN`` — takes priority over a trailing
#: parenthetical when both are present).
_QUOTED_SUBSTRING_PATTERN = re.compile(r'"([^"]+)"')

#: The canonical Cockburn level spellings → stereotypes (rulebook §2.3,
#: case-insensitive; anything else → no stereotype, never a failure).
_LEVEL_STEREOTYPES: dict[str, str] = {
    "summary": "<<summary>>",
    "user goal": "<<user goal>>",
    "subfunction": "<<subfunction>>",
}

#: The ordered-list marker mdformat renders on the first line of a step/
#: extension item (``3. ``/``10. ``) — stripped by the §2.9.2 pipeline.
_MARKER_PATTERN = re.compile(r"^\d+[.)] ")

#: An extension item containing this phrase (standalone or embedded,
#: case-insensitive) is the fragment's resumption note, not a message
#: (rulebook §2.9.7).
_RESUMPTION_PATTERN = re.compile(r"\b(?:return|continue) to step \d+\b", re.IGNORECASE)

#: A ``Related Use Cases`` reference: the ``UC`` tag + the shared
#: reference-tag separator + a canonical uuid (the in-package case) or a
#: legacy ``UC-NNN`` number (unresolvable by definition — rulebook §2.8).
#: Mirrors the UC branch of ``general.tools._references._REFERENCE_PATTERN``
#: (the parity is pinned by the test suite), plus the legacy digit form.
_UC_REFERENCE_PATTERN = re.compile(
    r"\bUC[ \t-]+("
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])"
    r"|\d+"
    r")",
    re.IGNORECASE,
)

#: The frozen package title (rulebook §2.7 item 1).
_PACKAGE_TITLE = "UC Package"

#: The frozen package layout (rulebook §2.7 item 2).
_PACKAGE_DIRECTION = "left to right direction"


def _actor_label(text: str) -> str:
    """Derive a clean PlantUML label from free-text actor description (rulebook §2.1).

    Port of v1's ``_actor_label`` (``uc/models/v1/uc_diagram.py``): the first
    double-quoted substring wins (priority over a trailing parenthetical);
    otherwise everything before the first ``" ("``; otherwise the text
    as-is, stripped.
    """
    assert isinstance(text, str), type(text)
    quoted = _QUOTED_SUBSTRING_PATTERN.search(text)
    if quoted is not None:
        result = quoted.group(1).strip()
        return result

    paren_index = text.find(" (")
    if paren_index != -1:
        result = text[:paren_index].strip()
        return result

    result = text.strip()
    return result


def _sanitize(text: str) -> str:
    """Quote sanitisation (rulebook §2.4): an embedded ``"`` becomes ``#quot;``."""
    assert isinstance(text, str), type(text)
    result = text.replace('"', "#quot;")
    return result


def _single_line(text: str) -> str:
    """Single-line escaping for one-PlantUML-line content (rulebook §2.4):
    sanitise, then emit literal newlines as the two-character ``\\n``."""
    assert isinstance(text, str), type(text)
    result = _sanitize(text).replace("\n", "\\n")
    return result


def _level_stereotype(use_case: UseCase) -> str | None:
    """The §2.3 level stereotype (case-insensitive normalisation; None when unrecognised)."""
    paragraphs = use_case.characteristic_information.level.body
    if not paragraphs:
        result: str | None = None
        return result
    key = str(paragraphs[0]).strip().lower()
    result = _LEVEL_STEREOTYPES.get(key)
    return result


def _first_sentence(text: str) -> str:
    """The first sentence: the first line, up to the first ``". "`` or its end (rulebook §2.2)."""
    line = text.split("\n", 1)[0]
    period_index = line.find(". ")
    result = line[:period_index] if period_index != -1 else line
    return result


def _system_label(use_case: UseCase) -> str:
    """The system participant label: the ``Scope`` first sentence, §2.1-cleaned (rulebook §2.2)."""
    paragraphs = use_case.characteristic_information.scope.body
    if not paragraphs:
        result = ""
        return result
    result = _actor_label(_first_sentence(str(paragraphs[0]).strip()))
    return result


@dataclass(frozen=True)
class _Participant:
    """One declared sequence participant (rulebook §2.9.1).

    Attributes:
        label: the cleaned label (the ``actor``/``participant`` declaration text).
        alias: the label itself when bare-identifier, else the positional ``p{N}``.
        keyword: ``"actor"`` for actor participants, ``"participant"`` for the system.
        index: the 1-based declaration position.
    """

    label: str
    alias: str
    keyword: str
    index: int


def _participants(use_case: UseCase) -> tuple[list[_Participant], _Participant | None]:
    """The declaration-ordered participants + the system participant (rulebook §2.9.1).

    Order: primary actor, secondary actors in document order, system last —
    deduplicated by cleaned label (first occurrence wins its slot; an actor
    whose label equals the system label is a single participant, and the
    system receiver always resolves to it).
    """
    info = use_case.characteristic_information
    order: list[tuple[str, str]] = []  # (cleaned label, keyword)
    seen: set[str] = set()

    def add(label: str, keyword: str) -> None:
        if label and label not in seen:
            seen.add(label)
            order.append((label, keyword))

    primary = info.primary_actor.body
    if primary:
        add(_actor_label(str(primary[0]).strip()), "actor")
    for item in info.secondary_actors.items if info.secondary_actors is not None else []:
        add(_actor_label(item.text), "actor")

    system_label = _system_label(use_case)
    if system_label and system_label not in seen:
        add(system_label, "participant")

    participants: list[_Participant] = []
    system: _Participant | None = None
    for position, (label, keyword) in enumerate(order, start=1):
        alias = label if _BARE_ALIAS_PATTERN.match(label) else f"p{position}"
        participant = _Participant(label=label, alias=alias, keyword=keyword, index=position)
        participants.append(participant)
        if system is None and label == system_label:
            system = participant

    return participants, system


def _distinct_actor_labels(use_case: UseCase) -> list[str]:
    """The distinct cleaned actor labels, primary first, then secondaries in
    document order (rulebook §2.1) — the usecase/actor-union order."""
    info = use_case.characteristic_information
    raw = [str(info.primary_actor.body[0]).strip()] if info.primary_actor.body else []
    raw.extend(item.text for item in (info.secondary_actors.items if info.secondary_actors is not None else []))

    labels: list[str] = []
    seen: set[str] = set()
    for item in raw:
        label = _actor_label(item)
        if label and label not in seen:
            seen.add(label)
            labels.append(label)
    return labels


# --- attribution (rulebook §2.9.3) ---------------------------------------------


def _word_boundary_prefix(label: str, text: str) -> bool:
    """Case-insensitive, word-boundary prefix test (the sender rule)."""
    pattern = re.compile(r"(?i)" + re.escape(label) + r"(?!\w)")
    return pattern.match(text) is not None


def _sender(text: str, participants: list[_Participant]) -> _Participant | None:
    """The longest cleaned participant label that is a word-boundary prefix of ``text``."""
    best: _Participant | None = None
    best_length = 0
    for participant in participants:
        if len(participant.label) > best_length and _word_boundary_prefix(participant.label, text):
            best = participant
            best_length = len(participant.label)
    return best


def _receiver(
    text: str,
    sender: _Participant,
    participants: list[_Participant],
    system: _Participant | None,
) -> _Participant:
    """The first sender-distinct participant label in text-position order, else the system.

    A sender-distinct label hit wins at the earliest text position (ties break
    on declaration order); with no hit, the receiver is the system — a
    self-message when the sender is the system (rulebook §2.9.3).
    """
    best: _Participant | None = None
    best_position = -1
    for participant in participants:
        if participant is sender:
            continue
        pattern = re.compile(r"(?i)(?<!\w)" + re.escape(participant.label) + r"(?!\w)")
        match = pattern.search(text)
        if match is None:
            continue
        if (
            best is None
            or match.start() < best_position
            or (match.start() == best_position and participant.index < best.index)
        ):
            best = participant
            best_position = match.start()
    if best is not None:
        return best
    # no sender-distinct label in the text → the system (a self-message when
    # the sender is the system)
    assert system is not None  # a use case without a system participant cannot be attributed
    return system


# --- the step decomposition pipeline (rulebook §2.9.2) ---------------------------


def _decompose(extent: str) -> tuple[str, str]:
    """Marker strip + lead-paragraph split + dedent (rulebook §2.9.2, on ``str(item)``).

    Returns ``(lead, continuation)``: the lead paragraph (message text — from
    the marker-stripped first line up to the first blank line, lazy
    continuation lines included) and everything after the first blank line,
    dedented by the stripped marker's width (``""`` when there is none).
    """
    assert isinstance(extent, str), type(extent)
    lines = extent.split("\n")
    first_line = lines[0]
    marker_match = _MARKER_PATTERN.match(first_line)
    marker_width = marker_match.end() if marker_match is not None else 0
    lead_lines: list[str] = [first_line[marker_width:]]
    position = 1
    while position < len(lines) and lines[position].strip() != "":
        line = lines[position]
        lead_lines.append(line[marker_width:] if len(line) >= marker_width else line.strip())
        position += 1
    lead = "\n".join(lead_lines)

    continuation_lines = lines[position + 1 :] if position < len(lines) else []
    dedented: list[str] = []
    for line in continuation_lines:
        if line.strip() == "":
            dedented.append("")
        elif marker_width and line.startswith(" " * marker_width):
            dedented.append(line[marker_width:])
        else:
            dedented.append(line.lstrip(" "))
    continuation = "\n".join(dedented)

    return lead, continuation


def _note_block(content_lines: list[str], *, attached: bool, anchor: str) -> list[str]:
    """One note block (frozen format): ``note right`` when attached to a
    message, ``note left of {anchor}`` when there is no message to attach to
    (rulebook §2.9.6, amended 2026-10-05 — the real 1.2026.8 parser rejects
    bare ``note``; amended 2026-10-06 — a bare note after a self-message's
    note tile with no intervening non-self message crashes 1.2026.8, and a
    bare note before the first message silently drops its text, so the
    unanchored notes are anchored on ``anchor``, the primary actor's §2.9.1
    declaration alias). Content lines are pre-indented; blank lines stay
    truly empty."""
    header = "note right" if attached else f"note left of {anchor}"
    block = [header]
    block.extend(content_lines)
    block.append("end note")
    return block


def _note_lines(content: str) -> list[str]:
    """The note content lines (2-space indented; a blank line stays truly empty)."""
    lines = content.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    return [f"  {line}" if line else "" for line in lines]


def _declaration_line(participant: _Participant) -> str:
    """The §2.9.1 declaration: bare label as its own alias, else quoted + ``as p{N}``."""
    if participant.alias == participant.label:
        result = f"{participant.keyword} {participant.label}"
    else:
        result = f'{participant.keyword} "{_sanitize(participant.label)}" as {participant.alias}'
    return result


# --- renderer 1: the per-UC usecase diagram (rulebook §2.5–§2.6) ------------------


def render_uc_diagram(use_case: UseCase) -> str:
    """Render one parsed v2 use case to its PlantUML usecase diagram (rulebook §2.5).

    Layout (frozen): ``@startuml {title}`` (sanitised, not quoted), a blank
    line, the actor declarations (distinct cleaned labels, primary first,
    secondaries in document order — ``actor {label}`` when bare, else
    ``actor "{label}" as actor{N}`` with N the 1-based position), the usecase
    node (``usecase "{title}" as uc`` + the §2.3 stereotype on the same line
    when present), a blank line, one ``-->`` association per actor, a blank
    line, ``@enduml``. Ends with exactly one trailing newline.

    Pure and deterministic: no file I/O, no resolution — the ``Related Use
    Cases`` references do not appear in the single-UC diagram (package-edge
    input only, §2.8).
    """
    assert isinstance(use_case, UseCase), type(use_case)

    title = str(use_case.text).strip()
    names = _distinct_actor_labels(use_case)

    lines: list[str] = [f"@startuml {_sanitize(title)}", ""]
    aliases: dict[str, str] = {}
    for index, name in enumerate(names, start=1):
        alias = name if _BARE_ALIAS_PATTERN.match(name) else f"actor{index}"
        aliases[name] = alias
        lines.append(_declaration_actor_line(name, alias))

    stereotype = _level_stereotype(use_case)
    usecase_line = f'usecase "{_sanitize(title)}" as uc'
    if stereotype is not None:
        usecase_line += f" {stereotype}"
    lines.append(usecase_line)
    lines.append("")

    for name in names:
        lines.append(f"{aliases[name]} --> uc")

    lines.append("")
    lines.append("@enduml")
    result = "\n".join(lines).strip("\n") + "\n"
    return result


def _declaration_actor_line(name: str, alias: str) -> str:
    if alias == name:
        result = f"actor {name}"
    else:
        result = f'actor "{_sanitize(name)}" as {alias}'
    return result


# --- renderer 2: the multi-UC package diagram (rulebook §2.7–§2.8) ----------------


@dataclass(frozen=True)
class PackageDocument:
    """One package slot, in package order (rulebook §2.7).

    The renderer's pure input: the parsed document plus its id — the disk
    resolution (which document is on disk, which parses, which is in the
    package) is the caller's job (the Phase 120 tool / the Phase 130 CLI via
    ``general.tools._doc_paths`` / the uc read path). A slot whose
    ``use_case`` is ``None`` (exists but failed to parse) is skipped as a
    node; any reference to it takes the §2.8 unresolvable-note path. The
    optional ``path`` is caller metadata the renderer ignores — the CLI's
    all-mode skip warning names the skipped document by id, else by path
    (a ``list_uc`` failed row's id is ``None`` — the frontmatter is unreadable
    — but its resolved path always is; the 2026-10-08 actionable-warning fix).

    Attributes:
        id: the document's frontmatter uuid (``None`` when unknown).
        use_case: the parsed document, or ``None`` for a broken slot.
        path: the document's resolved on-disk path (``None`` when the caller
            does not carry one — the renderer never reads it).
    """

    id: str | None
    use_case: UseCase | None
    path: str | None = None


def _bullet_kind(bullet: str) -> str:
    """The frozen per-bullet edge kind (rulebook §2.8): the recognised start
    keyword (``subordinate:`` → include, ``superordinate:`` → superordinate,
    ``extension:`` → extend), else the ``<<extend>>`` literal → extend, else
    the default ``include``."""
    lowered = bullet.strip().lower()
    if lowered.startswith("subordinate:"):
        result = "include"
        return result
    if lowered.startswith("superordinate:"):
        result = "superordinate"
        return result
    if lowered.startswith("extension:"):
        result = "extend"
        return result
    if "<<extend>>" in lowered:
        result = "extend"
        return result
    result = "include"
    return result


def _segment_start_for(index: int, bullet: str, matches: list[re.Match[str]]) -> int:
    """The label-segment start for ``matches[index]`` (rulebook §2.8 walk):
    the end of the previous reference's closing ``)`` when it was
    parenthesised, else the previous token's end (bullet start for the first)."""
    if index == 0:
        return 0
    previous = matches[index - 1]
    if previous.start() > 0 and bullet[previous.start() - 1] == "(":
        paren_close = bullet.find(")", previous.end())
        return paren_close + 1 if paren_close != -1 else previous.end()
    return previous.end()


def _clean_label(segment: str, is_first: bool) -> str:
    """Trim, drop the leading ``{keyword}: `` (first reference only, when the
    bullet carries one), drop a leading ``,``, trim again (rulebook §2.8)."""
    label = segment.strip()
    if is_first:
        keyword_match = re.match(r"(?i)^(subordinate|superordinate|extension):\s*", label)
        if keyword_match is not None:
            label = label[keyword_match.end() :]
    label = label.lstrip(",").strip()
    return label


def _walk_labels(bullet: str, matches: list[re.Match[str]]) -> list[str]:
    """The per-reference inline labels, walking the bullet left to right
    (rulebook §2.8): the segment runs from the previous reference's closing
    ``)`` (or the bullet start) to the ``(`` immediately preceding the token
    (or the token start when not parenthesised)."""
    labels: list[str] = []
    for index, match in enumerate(matches):
        if match.start() > 0 and bullet[match.start() - 1] == "(":
            label_end = match.start() - 1
        else:
            label_end = match.start()
        segment = bullet[_segment_start_for(index, bullet, matches) : label_end]
        labels.append(_clean_label(segment, index == 0))
    return labels


def _edge_line(kind: str, this_alias: str, target_alias: str, label: str) -> str:
    """The frozen edge line (rulebook §2.8 table; ``{label}`` omitted when empty)."""
    if kind == "superordinate":
        edge = f"{target_alias} ..> {this_alias}"
        if label:
            edge += f" : {_sanitize(label)}"
        return edge
    if kind == "extend":
        edge = f"{target_alias} ..> {this_alias} : <<extend>>"
        if label:
            edge += f" {_sanitize(label)}"
        return edge
    # include (Subordinate: or the frozen default)
    edge = f"{this_alias} ..> {target_alias} : <<include>>"
    if label:
        edge += f" {_sanitize(label)}"
    return edge


def render_use_case_package(documents: list[PackageDocument]) -> str:
    """Render N parsed v2 use cases (the package) to one PlantUML package diagram.

    Layout (frozen, rulebook §2.7): ``@startuml UC Package``, the frozen
    ``left to right direction``, a blank line, the usecase nodes (one per
    parsed slot, package order — the title as alias when bare-identifier,
    else ``uc{N}`` with N the 1-based node position; the §2.3 stereotype on
    the same line when present — the 2026-10-08 collision fallback: a LATER
    document whose cleaned title collides with an already-assigned alias
    takes its positional alias instead, and a positional name already
    assigned by an earlier document's bare title increments past the
    assigned aliases, so the emitted aliases are always unique), the actor
    declarations (the deduplicated
    union of all documents' distinct cleaned labels, first-appearance order:
    document order, within a document primary then secondaries), a blank
    line, the associations (per document, per its own actor declaration
    order), the package edges (per document, per ``Related Use Cases``
    bullet, per reference in text order — rulebook §2.8), a blank line,
    ``@enduml``. Ends with exactly one trailing newline.

    Broken slots (``use_case is None``) are skipped as nodes; a reference
    emits an edge only when it resolves to a parsed slot of the package
    (the §2.8 emission condition — on disk + parses + in-package, all three
    edge kinds), else the deterministic unresolvable note. The render never
    fails on a reference.
    """
    assert isinstance(documents, list), type(documents)

    parsed: list[tuple[str | None, UseCase]] = [(doc.id, doc.use_case) for doc in documents if doc.use_case is not None]
    package_ids = {doc_id for doc_id, _ in parsed if doc_id is not None}

    lines: list[str] = [f"@startuml {_PACKAGE_TITLE}", _PACKAGE_DIRECTION, ""]

    usecase_aliases: dict[str | None, str] = {}
    assigned_aliases: set[str] = set()
    for position, (doc_id, use_case) in enumerate(parsed, start=1):
        title = str(use_case.text).strip()
        if _BARE_ALIAS_PATTERN.match(title) and title not in assigned_aliases:
            # the FIRST document with a given cleaned title keeps the bare
            # alias (the rulebook §2.7 item 4 scheme, amended 2026-10-08)
            alias = title
        else:
            # a LATER document whose cleaned title collides with an
            # already-assigned alias (or is not bare-identifier) takes the
            # positional alias `uc{N}` — N the 1-based position in the
            # rendered list, incremented past any already-assigned alias:
            # the only case where the positional name differs from the
            # position is an earlier document whose bare title literally
            # reads `uc{N}` (the 2026-10-08 collision fallback — the
            # emitted aliases stay unique, so the alias-targeted edges
            # `uc ..> uc` never address an ambiguous name)
            number = position
            alias = f"uc{number}"
            while alias in assigned_aliases:
                number += 1
                alias = f"uc{number}"
        assigned_aliases.add(alias)
        usecase_aliases[doc_id] = alias
        stereotype = _level_stereotype(use_case)
        node_line = f'usecase "{_sanitize(title)}" as {alias}'
        if stereotype is not None:
            node_line += f" {stereotype}"
        lines.append(node_line)

    actor_union: list[str] = []
    seen: set[str] = set()
    for _doc_id, use_case in parsed:
        for label in _distinct_actor_labels(use_case):
            if label not in seen:
                seen.add(label)
                actor_union.append(label)

    actor_aliases: dict[str, str] = {}
    for position, label in enumerate(actor_union, start=1):
        alias = label if _BARE_ALIAS_PATTERN.match(label) else f"actor{position}"
        actor_aliases[label] = alias
        lines.append(_declaration_actor_line(label, alias))

    lines.append("")

    for doc_id, use_case in parsed:
        target_alias = usecase_aliases.get(doc_id)
        if target_alias is None:
            continue
        for label in _distinct_actor_labels(use_case):
            lines.append(f"{actor_aliases[label]} --> {target_alias}")

    for doc_id, use_case in parsed:
        this_alias = usecase_aliases.get(doc_id)
        if this_alias is None:
            continue
        related = use_case.characteristic_information.related_use_cases
        if related is None:
            continue
        for item in related.items:
            bullet = item.text
            matches = list(_UC_REFERENCE_PATTERN.finditer(bullet))
            if not matches:
                continue
            kind = _bullet_kind(bullet)
            labels = _walk_labels(bullet, matches)
            for index, match in enumerate(matches):
                ref_id = match.group(1).lower()
                if ref_id in package_ids:
                    target_alias = usecase_aliases.get(ref_id)
                    if target_alias is None:
                        continue  # unreachable: in-package ids map to parsed slots
                    lines.append(_edge_line(kind, this_alias, target_alias, labels[index]))
                else:
                    # the §2.8 unresolvable note — one per reference, never a failure
                    lines.append(f'note bottom of {this_alias}: Unresolved UC reference: "{_sanitize(labels[index])}"')

    lines.append("")
    lines.append("@enduml")
    result = "\n".join(lines).strip("\n") + "\n"
    return result


# --- renderer 3: the sequence skeleton (rulebook §2.9) ----------------------------


def render_uc_sequence_skeleton(use_case: UseCase) -> str:
    """Render one parsed v2 use case to its deterministic sequence skeleton.

    Layout (frozen, rulebook §2.9 — no blank lines inside the step body; one
    blank line only where shown): ``@startuml {title}``, a blank line, the
    participant declarations (§2.9.1), a blank line, the preconditions note +
    blank line (when present), the trigger (virtual step 0, §2.9.5 — receiver
    fixed to the system) plus its continuation note, the steps 1..N in
    ordinal order (each: message or UNATTRIBUTED marker, continuation note,
    sub-variation notes, the extensions anchored at this step — §2.9.7), a
    blank line, the final notes (success then failed end conditions),
    ``@enduml``. Ends with exactly one trailing newline.

    Messages leading with no participant label are emitted as UNATTRIBUTED
    markers (§2.9.4 — the shared :mod:`plantuml.structure` constants); the
    agent flow (Phase 120) resolves them. Pure and deterministic.

    Raises
    ------
    AssertionError
        The primary actor's label cleans to empty under the §2.1 rule — the
        sequence skeleton is UNRENDERABLE (the primary actor's declaration
        alias anchors the §2.9.6 unanchored notes, so there is no degraded
        render; rulebook §2.9.1, amended 2026-10-08). The message is
        actionable (cause + fix hint), and it fires before any output is
        built.
    """
    assert isinstance(use_case, UseCase), type(use_case)

    info = use_case.characteristic_information
    # the unrenderable edge (rulebook §2.9.1, amended 2026-10-08): a
    # PARSEABLE document whose primary actor's label cleans to empty under
    # the §2.1 rule (the v2 schema requires a non-empty primary-actor
    # paragraph, not one that survives cleaning — e.g. a quoted substring
    # containing only whitespace) cannot be rendered as a sequence skeleton
    # — the primary actor's declaration alias anchors the §2.9.6 unanchored
    # notes, so there is no sensible degraded render. The hard failure stays,
    # made actionable (feat-27 cause + fix hint), and is checked before any
    # output is built.
    primary_paragraphs = info.primary_actor.body
    primary_label = _actor_label(str(primary_paragraphs[0]).strip()) if primary_paragraphs else ""
    if not primary_label:
        raise AssertionError(
            "the sequence skeleton cannot be rendered: the primary actor's label cleans to empty under "
            "the §2.1 cleaning rule (the v2 schema requires a non-empty primary-actor paragraph, not one "
            "that survives cleaning — e.g. a quoted substring containing only whitespace); fix: give the "
            "primary actor a non-whitespace label — the skeleton's unanchored notes anchor on its §2.9.1 "
            "declaration alias, which does not exist without it (rulebook §2.9.1, amended 2026-10-08)"
        )
    title = str(use_case.text).strip()
    participants, system = _participants(use_case)
    # the unanchored-note anchor (rulebook §2.9.6, amended 2026-10-06): the
    # primary actor's §2.9.1 declaration alias — the first declared
    # participant (the non-empty cleaned primary label checked above
    # guarantees it)
    anchor = participants[0].alias

    lines: list[str] = [f"@startuml {_sanitize(title)}", ""]
    for participant in participants:
        lines.append(_declaration_line(participant))
    lines.append("")

    # the preconditions note (top, unanchored — `note left of {anchor}`) + blank line (when present)
    preconditions = info.preconditions.items
    if preconditions:
        content = "\n".join(entry.text for entry in preconditions)
        lines.extend(_note_block(_note_lines(content), attached=False, anchor=anchor))
        lines.append("")

    # the trigger (virtual step 0 — receiver fixed to the system)
    trigger_paragraphs = [str(paragraph).strip() for paragraph in info.trigger.body if str(paragraph).strip()]
    if trigger_paragraphs and system is not None:
        trigger_text = trigger_paragraphs[0]
        trigger_continuation = "\n".join(trigger_paragraphs[1:])
        sender = _sender(trigger_text, participants)
        if sender is None:
            lines.append(unattributed_trigger_marker(_single_line(trigger_text)))
            attached = False
        else:
            lines.append(f"{sender.alias} -> {system.alias}: {_single_line(trigger_text)}")
            attached = True
        if trigger_continuation:
            lines.extend(_note_block(_note_lines(trigger_continuation), attached=attached, anchor=anchor))

    # the extensions / sub-variations, grouped at their anchored step ordinals
    # (the v2 schema already validates the references — use_case.py:373)
    extensions = use_case.extensions.extensions if use_case.extensions is not None else []
    sub_variations = use_case.sub_variations.sub_variations if use_case.sub_variations is not None else []
    extension_anchors: dict[int, list[Extension]] = {}
    for extension in extensions:
        reference_match = re.match(r"^Extension (\d+)([a-z]?)\.", extension.text)
        assert reference_match is not None  # the @alias regex guarantees the shape
        # the anchor is the leading digits only — the optional letter is never
        # checked against the step ordinals (the model validator's own rule)
        extension_anchors.setdefault(int(reference_match.group(1)), []).append(extension)

    sub_variation_by_step: dict[int, list[SubVariation]] = {}
    for sub_variation in sub_variations:
        step_match = re.match(r"^Step (\d+):", sub_variation.text)
        assert step_match is not None  # the @alias regex guarantees the shape
        sub_variation_by_step.setdefault(int(step_match.group(1)), []).append(sub_variation)

    # the steps 1..N in ordinal order (the 1-based ordinal — never the marker)
    for ordinal, item in enumerate(use_case.main_success_scenario.steps, start=1):
        extent = str(item).rstrip("\n")
        lead, continuation = _decompose(extent)
        sender = _sender(lead, participants)
        if sender is None:
            lines.append(unattributed_step_marker(ordinal, _single_line(lead)))
            attached = False
        else:
            receiver = _receiver(lead, sender, participants, system)
            lines.append(f"{sender.alias} -> {receiver.alias}: {_single_line(lead)}")
            attached = True
        if continuation:
            lines.extend(_note_block(_note_lines(continuation), attached=attached, anchor=anchor))
        for sub_variation in sub_variation_by_step.get(ordinal, []):
            content = [sub_variation.text]
            content.extend(entry.text for entry in sub_variation.items)
            lines.extend(_note_block(_note_lines("\n".join(content)), attached=attached, anchor=anchor))
        for extension in extension_anchors.get(ordinal, []):
            lines.extend(_extension_fragment(extension, participants, system, anchor))

    lines.append("")

    # the final notes: success end condition, then failed (document order)
    for section in (info.success_end_condition, info.failed_end_condition):
        if section is not None and section.items:
            content = "\n".join(entry.text for entry in section.items)
            lines.extend(_note_block(_note_lines(content), attached=False, anchor=anchor))

    lines.append("@enduml")
    result = "\n".join(lines).strip("\n") + "\n"
    return result


def _extension_fragment(
    extension: Extension,
    participants: list[_Participant],
    system: _Participant | None,
    anchor: str,
) -> list[str]:
    """One ``alt`` fragment (frozen, rulebook §2.9.7): the condition header,
    the items in order (the same pipeline as a main step), the resumption
    notes (full item text — no message; ``note left of {anchor}`` when the
    resumption item is the fragment's first item), and the bare ``end``
    close (a single branch, no ``else``)."""
    reference_match = re.match(r"^Extension (\d+[a-z]?)\.\s+(.+)$", extension.text)
    assert reference_match is not None  # the @alias regex guarantees the shape
    extension_ref = reference_match.group(1)
    condition = reference_match.group(2)

    fragment: list[str] = [f"alt {_sanitize(condition)}"]
    has_message = False
    for ordinal, item in enumerate(extension.items, start=1):
        extent = str(item).rstrip("\n")
        lead, continuation = _decompose(extent)
        if _RESUMPTION_PATTERN.search(extent):
            # the resumption note: the item's COMPLETE text (marker stripped,
            # continuation included, single-line-escaped per §2.4) —
            # information-preserving, no message (rulebook §2.9.6, the
            # continuation included per the 2026-10-06 amendment)
            full_text = lead + (f"\n{continuation}" if continuation else "")
            fragment.extend(_note_block(_note_lines(_single_line(full_text)), attached=has_message, anchor=anchor))
            continue
        sender = _sender(lead, participants)
        if sender is None:
            fragment.append(unattributed_ext_marker(extension_ref, ordinal, _single_line(lead)))
            attached = False
        else:
            receiver = _receiver(lead, sender, participants, system)
            fragment.append(f"{sender.alias} -> {receiver.alias}: {_single_line(lead)}")
            attached = True
        has_message = True
        if continuation:
            fragment.extend(_note_block(_note_lines(continuation), attached=attached, anchor=anchor))
    fragment.append("end")
    return fragment
