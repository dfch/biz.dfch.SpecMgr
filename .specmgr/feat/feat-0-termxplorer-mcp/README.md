---
created: '2026-08-26 00:00:00.000Z'
id: feat-0-termxplorer-mcp
status: planning
updated: '2026-09-04 22:07:15.000Z'
version: 1.0.0
---

# Feature: MCP server for the tekom TermXplorer terminology database

## Plan

### Overview

An MCP server that lets agents query the tekom terminology database
(`https://tekom.termtechnologies.com/`, a TermXplorer 25.5 instance) to
validate technological terms against the agreed tekom glossary (preferred /
admitted / do-not-use designations, definitions, equivalents).

This folder currently holds **research findings only** (see `findings.md`,
the detailed results of the 2026-08-26 API investigation of the
TermXplorer instance: system identification, official API situation,
official data model, the verified internal RPC interface, account
permission profile, risks, and open questions for the MCP design). The
requirements/acceptance criteria/task list below are placeholders pending
the decision to draft the full MCP implementation plan.

### Requirements

- REQ-001: Define the concrete requirements for the TermXplorer MCP server once the implementation plan is drafted (see `findings.md`).

### Acceptance Criteria

- [ ] ACC-001: A full implementation plan (requirements, acceptance criteria, design, task list) has been drafted in this README, replacing this placeholder section.

### Scope

#### Included

- The black-box research and API investigation of the tekom TermXplorer instance, documented in `findings.md`.

#### Explicitly Out Of Scope

- Implementation of the MCP server itself, until the implementation plan is drafted and approved.

### Task List

#### Phase 0: Research

- [x] Task 0.1: Complete the black-box API investigation of tekom.termtechnologies.com (read-only, with the public `tekom_EN` demo credentials) and document findings in `findings.md`.

#### Phase 1: Implementation Planning

- [ ] Task 1.1: Draft the MCP server implementation plan (requirements, acceptance criteria, design, task list) in this README, based on `findings.md`.

## Progress

### Current Status

**As of 2026-08-26**: Investigation done, findings documented in
`findings.md`. Awaiting the decision to draft the MCP implementation plan.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-26 22:30:00.000+02:00 - Investigation completed

Completed the black-box API investigation of tekom.termtechnologies.com
(read-only, with the public `tekom_EN` demo credentials); findings written
to `findings.md`. Next: draft the MCP server implementation plan in this
README once requested.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-26 00:00:00.000Z - Findings documented in the feature folder

Document the findings in this feature folder (`findings.md`) rather than
in `docs/` -- this is development planning input for the upcoming MCP
feature, per the `.specmgr/` convention.
