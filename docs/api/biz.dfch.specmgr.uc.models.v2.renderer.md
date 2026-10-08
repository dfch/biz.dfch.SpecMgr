# `biz.dfch.specmgr.uc.models.v2.renderer`

Deterministic UC → PlantUML renderers (feat-185-uc-diagrams, Phase 110).

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

## Classes

### `PackageDocument`

One package slot, in package order (rulebook §2.7).

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


### `_Participant`

One declared sequence participant (rulebook §2.9.1).

Attributes:
    label: the cleaned label (the ``actor``/``participant`` declaration text).
    alias: the label itself when bare-identifier, else the positional ``p{N}``.
    keyword: ``"actor"`` for actor participants, ``"participant"`` for the system.
    index: the 1-based declaration position.


## Functions

### `_actor_label(text: 'str') -> 'str'`

Derive a clean PlantUML label from free-text actor description (rulebook §2.1).

Port of v1's ``_actor_label`` (``uc/models/v1/uc_diagram.py``): the first
double-quoted substring wins (priority over a trailing parenthetical);
otherwise everything before the first ``" ("``; otherwise the text
as-is, stripped.


### `_bullet_kind(bullet: 'str') -> 'str'`

The frozen per-bullet edge kind (rulebook §2.8): the recognised start
keyword (``subordinate:`` → include, ``superordinate:`` → superordinate,
``extension:`` → extend), else the ``<<extend>>`` literal → extend, else
the default ``include``.


### `_clean_label(segment: 'str', is_first: 'bool') -> 'str'`

Trim, drop the leading ``{keyword}: `` (first reference only, when the
bullet carries one), drop a leading ``,``, trim again (rulebook §2.8).


### `_declaration_actor_line(name: 'str', alias: 'str') -> 'str'`


### `_declaration_line(participant: '_Participant') -> 'str'`

The §2.9.1 declaration: bare label as its own alias, else quoted + ``as p{N}``.


### `_decompose(extent: 'str') -> 'tuple[str, str]'`

Marker strip + lead-paragraph split + dedent (rulebook §2.9.2, on ``str(item)``).

Returns ``(lead, continuation)``: the lead paragraph (message text — from
the marker-stripped first line up to the first blank line, lazy
continuation lines included) and everything after the first blank line,
dedented by the stripped marker's width (``""`` when there is none).


### `_distinct_actor_labels(use_case: 'UseCase') -> 'list[str]'`

The distinct cleaned actor labels, primary first, then secondaries in
document order (rulebook §2.1) — the usecase/actor-union order.


### `_edge_line(kind: 'str', this_alias: 'str', target_alias: 'str', label: 'str') -> 'str'`

The frozen edge line (rulebook §2.8 table; ``{label}`` omitted when empty).


### `_extension_fragment(extension: 'Extension', participants: 'list[_Participant]', system: '_Participant | None', anchor: 'str') -> 'list[str]'`

One ``alt`` fragment (frozen, rulebook §2.9.7): the condition header,
the items in order (the same pipeline as a main step), the resumption
notes (full item text — no message; ``note left of {anchor}`` when the
resumption item is the fragment's first item), and the bare ``end``
close (a single branch, no ``else``).


### `_first_sentence(text: 'str') -> 'str'`

The first sentence: the first line, up to the first ``". "`` or its end (rulebook §2.2).


### `_level_stereotype(use_case: 'UseCase') -> 'str | None'`

The §2.3 level stereotype (case-insensitive normalisation; None when unrecognised).


### `_note_block(content_lines: 'list[str]', *, attached: 'bool', anchor: 'str') -> 'list[str]'`

One note block (frozen format): ``note right`` when attached to a
message, ``note left of {anchor}`` when there is no message to attach to
(rulebook §2.9.6, amended 2026-10-05 — the real 1.2026.8 parser rejects
bare ``note``; amended 2026-10-06 — a bare note after a self-message's
note tile with no intervening non-self message crashes 1.2026.8, and a
bare note before the first message silently drops its text, so the
unanchored notes are anchored on ``anchor``, the primary actor's §2.9.1
declaration alias). Content lines are pre-indented; blank lines stay
truly empty.


### `_note_lines(content: 'str') -> 'list[str]'`

The note content lines (2-space indented; a blank line stays truly empty).


### `_participants(use_case: 'UseCase') -> 'tuple[list[_Participant], _Participant | None]'`

The declaration-ordered participants + the system participant (rulebook §2.9.1).

Order: primary actor, secondary actors in document order, system last —
deduplicated by cleaned label (first occurrence wins its slot; an actor
whose label equals the system label is a single participant, and the
system receiver always resolves to it).


### `_receiver(text: 'str', sender: '_Participant', participants: 'list[_Participant]', system: '_Participant | None') -> '_Participant'`

The first sender-distinct participant label in text-position order, else the system.

A sender-distinct label hit wins at the earliest text position (ties break
on declaration order); with no hit, the receiver is the system — a
self-message when the sender is the system (rulebook §2.9.3).


### `_sanitize(text: 'str') -> 'str'`

Quote sanitisation (rulebook §2.4): an embedded ``"`` becomes ``#quot;``.


### `_segment_start_for(index: 'int', bullet: 'str', matches: 'list[re.Match[str]]') -> 'int'`

The label-segment start for ``matches[index]`` (rulebook §2.8 walk):
the end of the previous reference's closing ``)`` when it was
parenthesised, else the previous token's end (bullet start for the first).


### `_sender(text: 'str', participants: 'list[_Participant]') -> '_Participant | None'`

The longest cleaned participant label that is a word-boundary prefix of ``text``.


### `_single_line(text: 'str') -> 'str'`

Single-line escaping for one-PlantUML-line content (rulebook §2.4):
sanitise, then emit literal newlines as the two-character ``\n``.


### `_system_label(use_case: 'UseCase') -> 'str'`

The system participant label: the ``Scope`` first sentence, §2.1-cleaned (rulebook §2.2).


### `_walk_labels(bullet: 'str', matches: 'list[re.Match[str]]') -> 'list[str]'`

The per-reference inline labels, walking the bullet left to right
(rulebook §2.8): the segment runs from the previous reference's closing
``)`` (or the bullet start) to the ``(`` immediately preceding the token
(or the token start when not parenthesised).


### `_word_boundary_prefix(label: 'str', text: 'str') -> 'bool'`

Case-insensitive, word-boundary prefix test (the sender rule).


### `render_uc_diagram(use_case: 'UseCase') -> 'str'`

Render one parsed v2 use case to its PlantUML usecase diagram (rulebook §2.5).

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


### `render_uc_sequence_skeleton(use_case: 'UseCase') -> 'str'`

Render one parsed v2 use case to its deterministic sequence skeleton.

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


### `render_use_case_package(documents: 'list[PackageDocument]') -> 'str'`

Render N parsed v2 use cases (the package) to one PlantUML package diagram.

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

