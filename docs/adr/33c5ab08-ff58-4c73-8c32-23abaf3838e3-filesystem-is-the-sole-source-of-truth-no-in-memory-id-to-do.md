---
status: accepted
decision-makers: dfch
id: 33c5ab08-ff58-4c73-8c32-23abaf3838e3
version: 1.0.0
---

# Filesystem is the sole source of truth: no in-memory id-to-document cache

## Context and Problem Statement

The MCP server is a long-running process. When the LLM or a human edits an ADR file directly (outside the MCP tools), the server's in-memory state becomes stale. The question is: should the MCP server maintain an in-memory cache of parsed Adr objects keyed by id, or should it always re-read from disk?

## Decision Drivers

Correctness under concurrent hand-edits and LLM-driven edits; simplicity and predictability (no cache invalidation logic); no staleness problems.

## Considered Options

Server-side cache (id → parsed Adr object, shared across tool calls) vs. re-read/re-parse/re-render/re-write on every tool call.

## Decision Outcome

The `.md` file on disk is the sole source of truth. Every MCP tool call re-reads the current on-disk state, re-parses it via the schema's parser, applies the mutation through in-memory Pydantic models, validates the result, re-renders the full file deterministically, and writes the file back. No in-memory cache of parsed documents is maintained. This ensures that hand-edits by users always see the latest state, and concurrent edits are safe (each tool call gets a fresh read of the current file).

### Consequences

Guaranteed correctness under concurrent edits (human and LLM). No cache invalidation logic needed. Trade-off: every tool call includes I/O and parsing overhead. At expected ADR-repo scale (dozens to low hundreds of files), this overhead is acceptable; the filesystem scan is cheap enough.

## More Information

File I/O and parsing are centralized in adr/tools/_io.py (read_adr, write_adr, load_by_id) and adr/tools/_paths.py (find_adr_path for id-to-path resolution via fresh directory scan).
