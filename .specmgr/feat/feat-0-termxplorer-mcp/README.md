---
created: '2026-08-26 00:00:00.000Z'
id: feat-0-termxplorer-mcp
status: planning
updated: '2026-08-26 00:00:00.000Z'
version: 1.0.0
---

# Feature: MCP server for the tekom TermXplorer terminology database

## Plan

### Overview

An MCP server that lets agents query the tekom terminology database
(`https://tekom.termtechnologies.com/`, a TermXplorer 25.5 instance) to
validate technological terms against the agreed tekom glossary (preferred /
admitted / do-not-use designations, definitions, equivalents).

This folder currently holds **research findings only**. The implementation
plan (requirements, acceptance criteria, design, task list) is **not yet
written** and will be added here later, based on `findings.md`.

### Related artifacts

- `findings.md` — detailed results of the 2026-08-26 API investigation of
  the TermXplorer instance (system identification, official API situation,
  official data model, the verified internal RPC interface, account
  permission profile, risks, open questions for the MCP design).

## Progress

### Current Status

**As of 2026-08-26**: Investigation done, findings documented in
`findings.md`. Awaiting the decision to draft the MCP implementation plan.

### Recent Updates

#### Update 2026-08-26T22:30:00+02:00 (newest)

- Completed: black-box API investigation of tekom.termtechnologies.com
  (read-only, with the public `tekom_EN` demo credentials); findings
  written to `findings.md`.
- Next: draft the MCP server implementation plan in this README once
  requested.

### Decisions Made

- **2026-08-26**: Document the findings in this feature folder
  (`findings.md`) rather than in `docs/` — this is development planning
  input for the upcoming MCP feature, per the `.specmgr/` convention.
