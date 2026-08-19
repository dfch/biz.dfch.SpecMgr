---
id: feat-NNN-slug
version: 1.0.0
status: planning
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Feature: [Feature Title]

## Plan

### Overview

Brief description of what this feature does and why it matters.

### Requirements

- REQ-001: [Functional requirement]
- REQ-002: [Non-functional requirement]
- REQ-003: [Constraint or dependency]

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — [testable condition]
- [ ] ACC-002: Verifies REQ-002 — [testable condition]
- [ ] ACC-003: Verifies REQ-003 — [testable condition]

### Scope

What is included in this feature:
- Item 1
- Item 2

What is explicitly out of scope:
- Item A
- Item B

### Dependencies

- Depends on: [other feat-NNN-slug, ADR id, or external]
- Blocks: [other feat-NNN-slug]

### Design Notes

Any architectural decisions, patterns, or design rationale relevant to this feature.

### Related ADRs

- [ADR id]: [Title]
- [ADR id]: [Title]

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: [Phase name]
- [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)
- [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10
- [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)

#### Phase 2: [Phase name]
- [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started
- [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of [YYYY-MM-DD]**: [Brief status summary]

### Blockers

- [ ] Blocker 1 — [description, impact, mitigation]
- [ ] Blocker 2 — [description, impact, mitigation]

(Remove this section if no blockers.)

### Recent Updates

If this section grows too long, move older entries to `history.md` in this
same folder and leave a pointer here, e.g.:
`See history.md for updates before YYYY-MM-DD.`

#### Update [YYYY-MM-DDTHH:mm:ssz] (newest)
- Completed: [what was done]
- Next: [what comes next]
- Notes: [any relevant context]

#### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)
- Completed: [what was done]
- Next: [what comes next]
- Notes: [any relevant context]

### Decisions Made

- **[YYYY-MM-DD]**: [Decision] — [Rationale]
- **[YYYY-MM-DD]**: [Decision] — [Rationale]

### Related PRs / Commits

- [PR #NNN](link): [description]
- [Commit hash](link): [description]
