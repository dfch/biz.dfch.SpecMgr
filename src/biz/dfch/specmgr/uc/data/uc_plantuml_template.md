@startuml Use Case Title

' The sequence-skeleton template (rulebook specmgr://uc/plantuml §2.9) — the shape
' render_uc_sequence_skeleton emits. Replace every {placeholder} with the use
' case's own content; delete the lines that do not apply. The trivial usecase
' diagram shape is frozen in the rulebook §2.6 instead (no template needed).

' --- participants (§2.9.1) — primary actor first, secondary actors in document
' order, the system last. A bare-identifier label is its own alias; anything
' else gets the positional alias p{N}. One declaration per distinct label.
actor "Primary actor" as p1
actor "Secondary actor" as p2
participant "System" as p3

' --- preconditions note (§2.9.6) — an anchored note-left top note (a bare
' note left after a self-message's note tile crashes PlantUML 1.2026.8, so
' unanchored notes are anchored on the primary actor's alias — p1 here), one
' line per precondition bullet. Delete this block when the use case has no
' preconditions.
note left of p1
  {precondition, one line per bullet}
end note

' --- trigger (§2.9.5) — virtual step 0: the first message, and its receiver is
' ALWAYS the system. When the trigger text leads with no participant label,
' the skeleton emits the marker form instead (see the note below the steps).
p1 -> p3: {trigger text}

' --- steps (§2.9.3) — one message line per main-scenario step, in 1-based
' ordinal order: {sender-alias} -> {receiver-alias}: {message text}. Sender =
' the longest participant label the text starts with; receiver = the first
' other participant label occurring in the text, else the system (a
' self-message when the sender is the system). A step the skeleton cannot
' attribute is NOT an arrow — it is a comment-line marker, one of the three
' frozen forms (shared constant in the import-free plantuml package):
'   - main steps:    " UNATTRIBUTED step {N}: <text>" (leading quote mark)
'   - extension items: " UNATTRIBUTED ext {N}{a} step {M}: <text>"
'   - trigger:       " UNATTRIBUTED trigger: <text>"
p1 -> p3: {step 1 text}
p3 -> p1: {step 2 text}

' --- continuation note (§2.9.2/§2.9.6) — a step whose source carries text
' beyond its lead paragraph gets a "note right" with the continuation verbatim
' (2-space indented lines). Delete when absent.
p1 -> p3: {step 3 text}
note right
  {continuation line, 2-space indented, verbatim}
end note

' --- extension fragments (§2.9.7) — one "alt" per extension, anchored at its
' step (emitted immediately after that step's message + notes): a single
' branch labelled by the extension's condition text, no else, closed by a
' bare end. Sibling extensions at the same step run in document order. An
' item containing "Return to step N" / "Continue to step N" (standalone or
' embedded) is the fragment's resumption note — the full item text (continuation
' included) as a note, NOT a message (an anchored note-left note —
' note left of p1 — when it is the fragment's first item).
alt {extension condition}
  p3 -> p1: {extension item text}
  note right
    Return to step 4.
  end note
end

' --- end-condition notes (§2.9.6) — anchored note-left final notes
' (note left of p1, the primary actor's alias — see the preconditions note
' above for why the unanchored form is anchored), success first, then
' failed, one line per bullet. Delete a block when its section is absent.
note left of p1
  {success end condition, one line per bullet}
end note
note left of p1
  {failed end condition, one line per bullet}
end note

@enduml
