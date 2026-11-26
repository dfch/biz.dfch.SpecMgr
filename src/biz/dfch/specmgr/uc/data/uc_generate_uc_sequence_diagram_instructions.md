# Generate the sequence diagram for use case $id

You are generating the **agent-owned** PlantUML sequence diagram for the use
case document with id `$id`. The deterministic part (participants, trigger,
notes, `alt` fragments, positionally pre-filled arrows) comes from the
`get_uc_sequence_skeleton` tool; **your** part is the attribution — replacing
every `UNATTRIBUTED` marker by an arrow decided from understanding the free
text — plus the validation loop. The normative spec for everything below is
the frozen rulebook; the steps narrate the flow and point at its sections,
they do not restate them.

## 1. Read the rulebook first

Read `specmgr://uc/plantuml` — the frozen UC → PlantUML mapping and
validation rulebook (mapping §2, validation chain §3, file layout §2.10,
Subfunction judgment §2.11, prompt contract §3.8). Do not proceed on memory
of the mapping; where this flow and the rulebook differ, the rulebook wins.

## 2. Build a TodoWrite plan

Build a `TodoWrite` list covering the steps below (read rulebook → read UC →
Subfunction judgment → skeleton → attribution → zero-marker check →
validation loop → host-native write → report) and keep it updated as you go.

## 3. Read the UC

Call `get_uc("$id")`.

- A parsed document: continue to step 4.
- A `ParseFailureResult` (the document exists but fails to parse): **stop
  and report** its `error` to the user — do not write any file. The
  document must be repaired first (the `repair` prompt / `doc-repairer`
  flow exists for that).
- `UcNotFoundError` (no use case with this id): stop and report.

## 4. Subfunction judgment (rulebook §2.11)

If the document's `### Level` is `Subfunction`, it gets its own sequence
diagram **only** when it adds interactions beyond its user goal's diagram —
otherwise the user goal's sequence diagram stands. Judge from the document
(its `## Related Use Cases` superordinate reference names the user goal;
that goal's own `diagrams/uc/<goal-id>.sequence.puml`, if present, is the
baseline). Whenever you are not confident, **ask the user via the `question`
tool** (record the question and the answer). If the outcome is "no own
diagram", stop and report — write nothing.

## 5. Fetch the skeleton

Call `get_uc_sequence_skeleton("$id")`. The result carries two classes of
message lines:

- **Pre-filled arrows** — the sender was a participant-label prefix of the
  message text (rulebook §2.9.3). They are **positional, not semantic**:
  you **MAY correct any pre-filled arrow** the free text shows to be wrong.
- **`UNATTRIBUTED` marker lines** — one of the three frozen forms
  (`' UNATTRIBUTED step {N}: <text>`,
  `' UNATTRIBUTED ext {N}{a} step {M}: <text>`,
  `' UNATTRIBUTED trigger: <text>`): messages the skeleton could not
  attribute. These are your work.

## 6. Attribute every UNATTRIBUTED marker

Replace each marker line by a real arrow
`{sender-alias} -> {receiver-alias}: {text}` by **understanding the free
text** (rulebook §2.9.3) — the message's own wording, its continuation
note, the extension's condition, the actors' roles, and the Goal in
Context. Use the aliases declared at the top of the skeleton (a quoted
label's alias is its `as p{N}` name). Whenever you are **not confident** —
the text does not clearly name a sender, two participants both fit, or an
extension item's actor is ambiguous — you **MUST ask the user via the
`question` tool** and record the question and the answer in the
walkthrough. Do not guess silently.

## 7. Zero-marker rule

The diagram is writable **only with zero `UNATTRIBUTED` markers
remaining**. Re-scan the full text before validating; if any marker line
survives, return to step 6 (a `question` case when the text is ambiguous).

## 8. Validation loop (rulebook §3.8)

Call `validate_plantuml(text)` with the current full diagram text, and
repeat until the write precondition holds:

1. **Structure pre-flight always** — the tool runs it first; on
   `structure_ok = false`, fix the reported `errors` (1-based line + cause
   + fix hint) and call again. The parser is never called on a structure
   red — keep known-broken content off the network.
2. **Green at the highest available layer** — with a validation source
   configured, `valid = true` (and `rendered = true`) at that source is
   the precondition for writing.
3. **`source_state` ≠ `ok` with a source set** — report `reason` and
   `fix_hint` to the user and **do not write**. A set-but-unavailable
   source is a hard failure (no fall-through to any other source,
   rulebook §3.3).
4. **All sources unset** — the structure-only floor (rulebook §3.4): you
   may write, but only with the `' validated: structure-only` comment as
   the file's **first line** (above `@startuml`), so the file's provenance
   is visible. This header is agent-path only; the deterministic CLI
   output never carries it.

## 9. Write the file (host-native)

Write the final text with **your host's own file-write tool** — **no
specmgr tool writes `.puml` files** (the sequence file is agent-owned,
rulebook §2.10). Path: `diagrams/uc/$id.sequence.puml` relative to the
working directory (create the `diagrams/uc/` directory as needed). The file
is git-tracked — but see step 10.

## 10. Never commit

Do **not** `git add` or commit the diagram file (or anything else) — commit
policy belongs to the user. Report instead: the written path, the
validation outcome (`checked_by`, `valid`/`rendered`, `source_state`),
every `question` you asked and its answer, and any pre-filled arrow you
corrected, with the reasoning for each.
