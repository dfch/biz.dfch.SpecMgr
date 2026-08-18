# Archived history — feat-12-qa-artifact

Older "Recent Updates" entries moved out of `README.md` to keep the live
Progress section focused on current state. Newest archived entry first.

#### Update 2026-08-18T11:15:00Z

- Completed: Restructured the Task List's execution model, modeled on
  feat-10's per-phase test-and-commit discipline
  (`.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md`) — added
  an explicit "Execution approach" note plus a mandatory phase-end task
  to every phase (0-6): extend/run that phase's unit tests, run the full
  pre-commit/quality gate, and update this README's Progress section,
  before a phase (or session) is considered done. This directly addresses
  the risk that implementation spans multiple sessions due to context
  size — a fresh-context session must be able to resume correctly from
  this file alone. Filled the two gaps where MCP-surface/cross-cutting
  testing was previously deferred to a terminal phase: Phase 4 gained a
  new Task 4.5 (`tests/qa/{tools,resources,prompts}/`) and Phase 5 gained
  a new Task 5.7 (`specmgr docs`/`mcp-docs`/`schema` drift check), each
  followed by its own phase-end task (4.6, 5.8). Phase 6 was repurposed
  from "Tests & Docs" to "Final cross-cutting verification" only
  (mirroring feat-10's own Phase 4), since per-phase testing now covers
  what Phase 6 previously deferred everything to. New tasks were appended
  with new numbers rather than renumbering existing tasks. Deliberately
  left Task 2.2's schema-generation sequencing (drafting `qa_schema.json`
  before any Pydantic model exists) unresolved for a separate pass, per
  explicit instruction, despite feat-10's own Decisions Made log
  recording an identical sequencing bug it had to fix (moved from its
  Phase 1 to Phase 2 as Task 2.5).
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

#### Update 2026-08-18T09:30:00Z

- Completed: Post-write review pass raised four loose ends, all resolved:
  (1) fixed a naming typo (`Requirement4` -> `Requirement`) and explicitly
  documented that its content is deliberately unspecified, arbitrary
  agent-authored data, not a gap to close later; (2) replaced `General`'s
  and `QaSection`'s hand-declared `comment: MarkdownComment | None` fields
  with inherited `MarkdownSection2WithComment`/`MarkdownSection3WithComment`
  mixins, matching TSK's/REQ's existing precedent; (3) verified the exact
  ISO 25010:2023 characteristic wording directly via the `specmgr:// iso25010` MCP resource (not just the packaged `.md` file) -- confirmed
  the schema's snake_case field names already correspond 1:1; (4) confirmed
  `Introduction`/`RawRequirements`'s implicit `AliasType.SPACE_SEPARATED`
  alias derivation is being kept as-is, intentionally, not changed.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

#### Update 2026-08-18T08:00:00Z

- Completed: Full planning/design discussion — schema shape iterated
  through several rounds (blockquote-as-question feasibility check,
  answer-content representation, `QaSection` field ordering, the
  `end_marker` generalization and its decorator-merge prerequisite), this
  `README.md` written.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation intentionally not started yet per explicit
  instruction — this commit is plan-only.
