---
classification: null
created: '2026-11-22T15:40:00.000+01:00'
id: feat-270-cnl-business-rules
status: planning
type: feat
updated: '2026-11-22T15:40:00.000+01:00'
version: 1.0.0
---

# Feature: CNL business rule and process authoring, validation and execution

## Plan

### Overview

GitHub issue #270. Domain experts write business rules and processes as controlled natural language (CNL). A deterministic parser validates them against a core type system and pluggable domain types. A FOSS engine on a subset of DMN and BPMN runs them. The CNL text and the executable model stay in sync through one canonical model. The goal is GOL 361a523d-bd30-4585-adac-3f6f3800aece. The elicitation is QA 0a69baf3-9881-422d-a49e-af93b5f15eec. This feature is the scoping step only. The capability itself is expected to live in its own repository and MCP server, not as a specmgr domain.

### Requirements

- REQ-001: The open questions of QA 0a69baf3-9881-422d-a49e-af93b5f15eec are answered or explicitly deferred.
- REQ-002: The location of the initiative (this repository or a new repository and MCP server) is decided in a DEC.
- REQ-003: The CNL approach, the standards subset (DMN, BPMN or a custom DSL) and the FOSS engine are decided, each with its rationale.

### Acceptance Criteria

- [ ] ACC-001: QA 0a69baf3-9881-422d-a49e-af93b5f15eec has no `TODO: answer pending` left, except items marked as deferred.
- [ ] ACC-002: A DEC records the location of the initiative.
- [ ] ACC-003: The CNL, standards and engine decisions exist as DECs and are referenced from GOL 361a523d-bd30-4585-adac-3f6f3800aece.

### Scope

#### Included

- Elicitation and architecture decisions for the initiative.
- The GOL and QA documents, and their move to the new repository if one is decided.

#### Explicitly Out Of Scope

- Any implementation: parser, type system, agent skills, engine integration.
- A new specmgr artifact type for business rules.

### Dependencies

#### Depends On

- None.

#### Blocks

- The implementation of the initiative.

### Design Notes

- eCH-0278 is an example of a pluggable domain type system only. The target domain is open.
- If a new repository is decided, the GOL and QA move there and are deleted here. No other artifact references them.

### Related Decisions

- None yet.

### Task List

#### Phase 100: Scoping

- [x] Task 100.100: Create issue #270 and this feature. Move the GOL and QA from branch feat-267-arch-rvw to this branch.
- [ ] Task 100.110: Answer or defer the open questions of QA 0a69baf3-9881-422d-a49e-af93b5f15eec.
- [ ] Task 100.120: Write the DEC on the location of the initiative.
- [ ] Task 100.130: Write the DECs on the CNL approach, the standards subset and the engine.

## Progress

### Current Status

**As of 2026-11-22**: Feature created. The GOL and QA are on this branch. Elicitation has not resumed since 2026-10-06.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22 14:40:00.000Z - Created

Feature created from GOL 361a523d-bd30-4585-adac-3f6f3800aece and QA 0a69baf3-9881-422d-a49e-af93b5f15eec, which were split off from branch feat-267-arch-rvw (unrelated scope there). Issue #270 opened.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22 14:40:00.000Z - Own branch, not part of feat-267

The GOL and QA were committed on feat-267-arch-rvw, which is about the architecture review model. They are cherry-picked here and reverted there, so the history of both branches stays intact.

### Related PRs / Commits

- Issue #270.
