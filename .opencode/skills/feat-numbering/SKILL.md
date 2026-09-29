---
name: feat-numbering
description: Use when authoring or revising a specmgr FEAT document's Task List -- defines the Phase NNN / Task NNN.MMM numbering scheme (3-digit, start 100, step 10, in-between insertion, permanent numbers) for `.specmgr/feat/<id>/README.md` plans.
---

# FEAT Phase/Task Numbering

Every specmgr FEAT document (`.specmgr/feat/<id>/README.md`) numbers its `### Task List` phases
and tasks with a stable, gap-friendly scheme, so a new phase or task can always be inserted
in-between without renumbering anything that already exists.

## The scheme

Task List numbering scheme: phases carry 3-digit zero-padded numbers starting at 100, step 10
(`Phase 100`, `Phase 110`, `Phase 120`, ...); each task line is `- [ ] Task NNN.MMM: {text}` (or
`- [x] ...` once done), where `NNN` is the enclosing phase's number and `MMM` is a 3-digit
zero-padded task number starting at 100, step 10, within its phase (`Task 100.100`, `Task 100.110`,
...). The schema enforces only the number SHAPES -- `#### Phase NNN: {title}` and the
`Task NNN.MMM: ` prefix -- not the step-10 increments, not uniqueness, and not the match between
a task's `NNN` and its enclosing phase's number: those are authoring conventions. Gaps are
deliberate: to insert a new phase or task, pick the number between its neighbours (e.g. `Phase 105`,
`Task 100.105`) so existing numbers never renumber; once assigned, a number is permanent, and
removals leave gaps.

## Fetch the authoritative references

Do not rely on memory -- fetch the packaged FEAT resources before drafting or revising a
`### Task List`:

- `specmgr://feat/template`: the full document shape, with `Phase 100` holding `Task 100.100`.
- `specmgr://feat/example`: a realistic two-phase task list, `Phase 100` (`Task 100.100`) and
  `Phase 110` (`Task 110.100`, `Task 110.110`).
- `specmgr://feat/schema`: the generated JSON Schema carrying the enforced `#### Phase NNN:
  {title}` heading and `Task NNN.MMM: ` item shapes.

## Adding a phase or task

- A new phase starts its own task series at 100: the first task of `Phase 110` is `Task 110.100`,
  never a continuation of the previous phase's numbers.
- Pick the number between its existing neighbours (e.g. `Phase 105` between `Phase 100` and
  `Phase 110`; `Task 100.105` between `Task 100.100` and `Task 100.110`) and insert the one new
  numbered line -- never renumber existing lines.
- A number is permanent once assigned; removing a phase or task leaves a gap on purpose.
- Legacy documents written before this scheme are handled by the follow-up migration TSK
  tsk-2687d267 -- do not reintroduce their legacy numbering shapes when adding or editing phases
  and tasks.
