---
status: accepted
decision-makers: dfch
id: 898bfcd0-85f9-462f-93a8-747bda4166c8
version: 1.0.0
---

# Author and edit ADRs only through MCP structured tools, never raw markdown

## Context and Problem Statement

ADRs must be created and edited by an LLM through an MCP server. The LLM could approach this in two ways: (1) directly manipulating raw markdown files and trusting the result will be valid, or (2) calling structured MCP tools that enforce the schema and handle all parsing/validation/rendering internally. Raw markdown editing is error-prone (missing frontmatter, malformed YAML, inconsistent heading structure) and difficult to validate without round-trip parsing.

## Decision Drivers

Reliability and correctness of generated ADRs; auditability of changes through structured tool calls; centralized schema validation to catch errors early; preventing malformed documents from being written to disk.

## Considered Options

LLM writes raw markdown files directly vs. LLM calls structured MCP tools (create_adr, update_section, option_create, etc.) that enforce schema and handle all file I/O.

## Decision Outcome

Expose only MCP tools (create_adr, update_frontmatter, update_section, set_status, option_list/create/read/update/delete, validate_adr). The LLM must use these tools; direct markdown editing is not available. Each tool re-reads the current on-disk state, applies the mutation through in-memory Pydantic models (ensuring schema compliance), validates the result, and writes back the full file deterministically. This ensures every edit round-trips through validation.

### Consequences

All ADR edits go through a single, auditable code path. Schema violations are caught immediately by Pydantic, before writing. The LLM cannot accidentally create malformed frontmatter or missing required sections. Trade-off: the LLM must learn the tool names and parameters rather than directly manipulating prose.

## More Information

See MCP tool definitions in `biz.dfch.specmgr.adr.tools`: create_adr, update_frontmatter, update_section, set_status, option_create, option_update, option_read, option_delete, option_list, get_adr, validate_adr.
