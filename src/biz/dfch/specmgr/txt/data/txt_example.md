---
created: '2026-10-20T08:15:42.804Z'
id: 9c8b7a6d-5e4f-4c3b-8a79-6d5c4b3a2918
status: done
type: txt
updated: '2026-10-24T19:23:51.078Z'
version: 1.0.0
---

# Gateway Incident Review Notes

Free-form review notes for the 2026-10-20 gateway incident. This document
uses the free-form text type on purpose: the body carries its own headings
and lists, and it cross-references the requirement the review was scoped
against as a free-floating reference line.

REQ deaddead-beef-beef-beef-deaddeadbeef: Revoke API key within 1s of agent action

## Findings

- The gateway logged the revocation request 40 ms after the agent action.
- The audit-log write added 180 ms of overhead on the critical path.
- The 1-second budget was met with margin under nominal load.

### Root Cause

The revocation endpoint serialized its audit-log write behind the response
commit; moving the write off the critical path removed the overhead.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-24 19:23:51.078Z - Review complete

All findings were confirmed against the production trace; the notes were
marked done.

### 2026-10-20 08:15:42.804Z - Initial draft created

First draft of the review notes, transcribed from the incident channel.
