---
status: proposed
decision-makers: dfch
id: e369ee2e-3353-4f92-991c-6367d76d832e
version: 1.0.0
---

# Organize development artifacts in .dfch-spec/ with feature-driven work units

## Context and Problem Statement

The project maintains two distinct documentation folders: `docs/` — published, generated documentation (API docs, ADRs, specifications) — and `doc/` — development progress notes, planning artifacts, research. This separation is unclear. Development artifacts (plans, progress tracking, work-unit status) need a structured, agent-friendly location that is: (1) separate from published documentation (`docs/`); (2) organized by feature/work-unit for easy agent reference; (3) generic enough to serve as a template for future projects using specmgr as a toolkit.

## Decision Drivers

- Agent-friendly reference paths: agents should reference specific feature paths inline (e.g., "See `.dfch-spec/feat/feat-001-adr-toc/README.md`"), keeping agent instructions lean and focused
- Toolkit reusability: structure should be generic enough for future projects adopting specmgr as a toolkit
- Clear separation of concerns: development artifacts must be distinct from published documentation
- Version control and auditability: development progress should be tracked in git with full history

## Considered Options

- `.dfch-spec/` structure with feature work units (feat-NNN-slug folders containing README.md + progress.md)

## Decision Outcome

Establish `.dfch-spec/` as the root folder for development artifacts, with a feature-driven structure using the naming convention `feat-NNN-slug` where `NNN` is the GitHub issue number and `slug` is a kebab-case description. Each feature folder contains a `README.md` (plan) and a `progress.md` (status tracking).

### Consequences

**Positive:**
- Agents can reference specific feature paths inline, keeping instructions lean and focused
- Clear separation: agents only read what's relevant to their task
- Structure is reusable for future projects adopting specmgr as a toolkit
- Development progress is version-controlled and auditable

**Negative:**
- Adds another top-level folder to the repo structure
- Requires discipline to keep progress.md updated (hand-maintained, not auto-generated)

## Pros and Cons of the Options

### Option 1: .dfch-spec structure

```
.dfch-spec/
├── feat/                          # Feature work units
│   └── feat-NNN-slug/             # One folder per GitHub issue
│       ├── README.md              # Feature plan (mandatory)
│       └── progress.md            # Status tracking (mandatory)
└── (other dirs as needed)
```

**File purposes:**
- `README.md` — Contains the complete feature plan: acceptance criteria, scope, dependencies, design notes, any pre-implementation research
- `progress.md` — Hand-maintained status log: current state, blockers, decisions made during implementation, links to related ADRs or PRs

**Template: README.md**

```markdown
# Feature: [Feature Title]

**GitHub Issue**: #NNN  
**Status**: [Planning | In Progress | Review | Done]

## Overview

Brief description of what this feature does and why it matters.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Scope

What is included in this feature:
- Item 1
- Item 2

What is explicitly out of scope:
- Item A
- Item B

## Dependencies

- Depends on: [other feat-NNN-slug, ADR id, or external]
- Blocks: [other feat-NNN-slug]

## Design Notes

Any architectural decisions, patterns, or design rationale relevant to this feature.

## Related ADRs

- [ADR id]: [Title]
- [ADR id]: [Title]
```

**Template: progress.md**

```markdown
# Progress: [Feature Title]

## Current Status

**As of [YYYY-MM-DD]**: [Brief status summary]

## Blockers

- [ ] Blocker 1 — [description, impact, mitigation]
- [ ] Blocker 2 — [description, impact, mitigation]

(Remove this section if no blockers.)

## Recent Updates

### [YYYY-MM-DD]
- Completed: [what was done]
- Next: [what comes next]
- Notes: [any relevant context]

### [YYYY-MM-DD]
- Completed: [what was done]
- Next: [what comes next]
- Notes: [any relevant context]

## Decisions Made

- **[YYYY-MM-DD]**: [Decision] — [Rationale]
- **[YYYY-MM-DD]**: [Decision] — [Rationale]

## Related PRs / Commits

- [PR #NNN](link): [description]
- [Commit hash](link): [description]
```
